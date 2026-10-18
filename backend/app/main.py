import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base, ensure_schema_compatibility
from app.api.routes_projects import router as projects_router
from app.api.routes_claims import router as claims_router
from app.api.routes_content import router as content_router
from app.api.routes_artifacts import router as artifacts_router
from app.api.routes_export import router as export_router
from app.api.routes_settings import router as settings_router

# Create SQLite database tables
Base.metadata.create_all(bind=engine)
ensure_schema_compatibility()

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"==================================================")
    print(f" {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f" Database: {settings.DATABASE_URL}")
    print(f" Storage Directory: {settings.STORAGE_DIR}")
    print(f" AI Provider: {settings.AI_PROVIDER}")
    print(f" TTS Engine: {settings.TTS_ENGINE}")
    print(f"==================================================")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Doctor-Led Metabolic Health Research-to-Content Pipeline for Steer",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local frontend dev server on any port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Include Routers
app.include_router(settings_router)
app.include_router(projects_router)
app.include_router(claims_router)
app.include_router(content_router)
app.include_router(artifacts_router)
app.include_router(export_router)

# Mount generated storage directory for direct static serving
settings.generated_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/generated", StaticFiles(directory=str(settings.generated_dir)), name="generated")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
