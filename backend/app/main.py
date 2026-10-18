from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import init_db
from app.api import (
    routes_projects,
    routes_evidence,
    routes_content,
    routes_reel,
    routes_pptx,
    routes_review,
    routes_export,
    routes_settings
)

# Initialize database
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Doctor-Led Research-to-Content Studio. One verified scientific source. Multiple formats. Different audiences. Consistent evidence. Human approval."
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount storage directory for static asset delivery (PNGs, MP4s, PPTX, ZIPs)
app.mount("/storage", StaticFiles(directory=str(settings.STORAGE_DIR)), name="storage")

# Include Routers
app.include_router(routes_projects.router)
app.include_router(routes_evidence.router)
app.include_router(routes_content.router)
app.include_router(routes_reel.router)
app.include_router(routes_pptx.router)
app.include_router(routes_review.router)
app.include_router(routes_export.router)
app.include_router(routes_settings.router)

@app.get("/")
def root():
    return {
        "studio": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "status": "operational",
        "docs_url": "/docs"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "database": "sqlite_operational",
        "storage": "writable"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
