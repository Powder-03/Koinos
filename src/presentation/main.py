import os
import json
import base64
import logging
from fastapi import FastAPI

from contextlib import asynccontextmanager
import firebase_admin
from firebase_admin import credentials
from src.infrastructure.database.connection import engine
from src.infrastructure.database.models import Base
from src.presentation.api.manual_router import router as manual_router
from src.presentation.api.voice_router import router as voice_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Firebase Init ---
    # Priority order:
    #   1. GOOGLE_APPLICATION_CREDENTIALS file path  (local dev / docker-compose)
    #   2. FIREBASE_CREDENTIALS_JSON env var          (Render / Railway / Fly.io)
    #   3. Application Default Credentials            (GCP only)
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

    if cred_path and os.path.exists(cred_path):
        logger.info("🔑 Firebase: loading credentials from file %s", cred_path)
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    elif cred_json:
        logger.info("🔑 Firebase: loading credentials from FIREBASE_CREDENTIALS_JSON env var")
        # Accept either raw JSON or base64-encoded JSON
        try:
            sa_dict = json.loads(cred_json)
        except json.JSONDecodeError:
            sa_dict = json.loads(base64.b64decode(cred_json))
        cred = credentials.Certificate(sa_dict)
        firebase_admin.initialize_app(cred)
    else:
        # Fallback — only works on GCP (Cloud Run / App Engine)
        logger.warning("⚠️ Firebase: no explicit credentials found — using Application Default Credentials")
        firebase_admin.initialize_app()

    # --- DB Tables ---
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

app = FastAPI(title="Koinos Expense Tracker", lifespan=lifespan)

# Mount endpoints
app.include_router(manual_router)
app.include_router(voice_router)

@app.api_route("/", methods=["GET", "HEAD"])
@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    """Lightweight health check — point your uptime bot here to prevent cold starts."""
    return {"status": "healthy", "service": "koinos-api"}
