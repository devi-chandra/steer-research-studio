from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def ensure_schema_compatibility() -> None:
    """Add new nullable/defaulted safety columns to an existing hackathon DB.

    This is deliberately small and idempotent; production would use Alembic.
    """
    inspector = inspect(engine)
    if "content_drafts" not in inspector.get_table_names():
        return
    existing = {column["name"] for column in inspector.get_columns("content_drafts")}
    additions = {
        "version": "INTEGER NOT NULL DEFAULT 1",
        "review_status": "VARCHAR(30) NOT NULL DEFAULT 'draft'",
        "approved_version": "INTEGER",
        "metadata_json": "JSON",
    }
    with engine.begin() as connection:
        for name, definition in additions.items():
            if name not in existing:
                connection.execute(text(f"ALTER TABLE content_drafts ADD COLUMN {name} {definition}"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
