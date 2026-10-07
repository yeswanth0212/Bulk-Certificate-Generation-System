from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy import text
from app.config import settings
from app.database import Base, engine
from app.api.v1.router import api_router

# Initialize Database Tables
Base.metadata.create_all(bind=engine)

# Auto-migrate schema for SQLite if new columns were added
def auto_migrate():
    with engine.connect() as conn:
        try:
            result = conn.execute(text("PRAGMA table_info(certificate_jobs)"))
            cols = [row[1] for row in result.fetchall()]
            if cols:
                if "signatory_name" not in cols:
                    conn.execute(text("ALTER TABLE certificate_jobs ADD COLUMN signatory_name VARCHAR(255) DEFAULT 'Dr. Alex Vance'"))
                if "signatory_title" not in cols:
                    conn.execute(text("ALTER TABLE certificate_jobs ADD COLUMN signatory_title VARCHAR(255) DEFAULT 'Director of Certification'"))
                conn.commit()
        except Exception:
            pass

auto_migrate()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="High-performance Bulk Certificate Generation API with Background Queue, Format Support & PDF/PNG Download.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Static Files Directory
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", include_in_schema=False)
def read_root():
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }
