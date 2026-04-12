from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.infrastructure.database.connection import engine
from src.infrastructure.database.models import Base
from src.presentation.api.manual_router import router as manual_router
from src.presentation.api.voice_router import router as voice_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup DB Tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Koinos Expense Tracker", lifespan=lifespan)

# Mount endpoints
app.include_router(manual_router)
app.include_router(voice_router)

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "dual-mode-expense"}
