import asyncio
import logging
from fastapi import FastAPI
from discord.ext import commands
from src.bot.events import setup_events
from src.bot.commands import setup_commands
from src.handlers.github_webhook import router as github_router
from config import config
from flask import Flask, request, jsonify
from discord_interactions import verify_key_decorator
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/discord-interaction', methods=['POST'])
@verify_key_decorator(os.getenv('DISCORD_PUBLIC_KEY'))
def discord_interaction():
    interaction = request.json
    
    if interaction["type"] == 1:  # PING
        return jsonify({
            "type": 1  # PONG
        })
    
    return jsonify({
        "type": 4,  # CHANNEL_MESSAGE_WITH_SOURCE
        "data": {
            "content": "Command received!"
        }
    })

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
    uvicorn.run(app, host="0.0.0.0", port=8000) 