import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.database import check_db_connection
from app.api.routes import auth, qr, call, pages

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Static files
static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# API routes first
app.include_router(auth.router)
app.include_router(qr.router)
app.include_router(call.router)

# Page routes last (catch-all like /v/{id})
app.include_router(pages.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/health/db", tags=["health"])
def health_db():
    if check_db_connection():
        return {"status": "ok", "database": "connected"}
    return {"status": "error", "database": "unreachable"}
