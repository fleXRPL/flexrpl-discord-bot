from fastapi import FastAPI
import logging
from config import config
from src.routes.discord import router as discord_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI with minimal settings
app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# Include the Discord router
app.include_router(discord_router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
