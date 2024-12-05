import asyncio
import os

import uvicorn
from dotenv import load_dotenv

from app import app
from bot.bot import FlexRPLBot

# Load environment variables
load_dotenv()

# Create bot instance
bot = FlexRPLBot()


async def start_bot():
    """Start the Discord bot."""
    try:
        await bot.start(os.getenv("DISCORD_BOT_TOKEN"))
    except Exception as e:
        print(f"Failed to start bot: {e}")
        raise


async def start_server():
    """Start the FastAPI server."""
    config = uvicorn.Config(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
    server = uvicorn.Server(config)
    await server.serve()


async def run_all():
    """Run both the bot and the server."""
    await asyncio.gather(start_bot(), start_server())


if __name__ == "__main__":
    asyncio.run(run_all())
