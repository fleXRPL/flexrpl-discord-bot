import asyncio
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from discord.ext import commands
from src.bot.events import setup_events
from src.bot.commands import setup_commands
from src.handlers.github_webhook import router as github_router
from config import config
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="fleXRPL Discord Bot")

# Initialize Discord bot
bot = commands.Bot(command_prefix="!")

@app.get("/")
async def health_check():
    """Health check endpoint for Railway"""
    return JSONResponse(
        content={
            "status": "healthy",
            "message": "Discord bot is running"
        },
        status_code=200
    )

@app.post("/discord-interaction")
async def discord_interaction(request: Request):
    interaction = await request.json()
    
    if interaction.get("type") == 1:  # PING
        return JSONResponse(content={"type": 1})  # PONG
    
    return JSONResponse(
        content={
            "type": 4,
            "data": {
                "content": "Command received!"
            }
        }
    )

@app.on_event("startup")
async def startup_event():
    """Initialize bot and start it in the background."""
    try:
        # Setup bot events and commands
        setup_events(bot)
        await setup_commands(bot)
        
        # Start bot in background
        asyncio.create_task(bot.start(config.DISCORD_TOKEN))
        logger.info("Bot started successfully")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

# Include routers
app.include_router(github_router, prefix="/webhook", tags=["webhooks"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    ) 