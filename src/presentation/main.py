import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
import firebase_admin
from firebase_admin import credentials
from src.infrastructure.database.connection import engine
from src.infrastructure.database.models import Base
from src.presentation.api.manual_router import router as manual_router
from src.presentation.api.voice_router import router as voice_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Firebase Init ---
    # Uses GOOGLE_APPLICATION_CREDENTIALS env var if set,
    # otherwise initializes with no credential (works in Google Cloud environments).
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # For Google Cloud Run / App Engine where default creds are available
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
