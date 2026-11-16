from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from .config import UPLOAD_ROOT, settings
from .database import Base, SessionLocal, engine
from .routers import admin, auth, properties, uploads
from .seed import seed_if_empty
from .services import damage_inference, gemini_vision, rentcast

# Must exist before StaticFiles is mounted (mount checks at import time).
(UPLOAD_ROOT / "property").mkdir(parents=True, exist_ok=True)

# Columns added after the first release. SQLite create_all() does not add columns
# to existing tables, so add any that are missing on startup.
_ADDED_PROPERTY_COLUMNS = {
    "gallery_images": "JSON",
    "image_rooms": "JSON",
    "photo_analyses": "JSON",
    "rehab_items": "JSON",
    "valuation": "JSON",
    "warnings": "JSON",
}


def _migrate_columns() -> None:
    existing = {c["name"] for c in inspect(engine).get_columns("properties")}
    with engine.begin() as conn:
        for name, sql_type in _ADDED_PROPERTY_COLUMNS.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE properties ADD COLUMN {name} {sql_type}"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    _migrate_columns()
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, version="1.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(properties.router, prefix="/api")
app.include_router(uploads.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.mount("/api/uploads", StaticFiles(directory=str(UPLOAD_ROOT)), name="uploads")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": "OffmarketStream",
        "damageModel": "loaded" if damage_inference.model_available() else "missing",
        "visionAi": settings.gemini_model if gemini_vision.configured() else "not configured",
        "marketData": "rentcast" if rentcast.configured() else "not configured",
    }
