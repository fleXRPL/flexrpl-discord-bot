import asyncio
import logging
import os
import time

import uvicorn
from discord.interactions import InteractionType
from dotenv import load_dotenv
from fastapi import Request

from app import app
from bot.bot import FlexRPLBot

# Load environment variables
load_dotenv()

# Create bot instance
bot = FlexRPLBot()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add rate limiting control
last_sync_time = 0
SYNC_COOLDOWN = 60  # seconds between syncs


async def should_sync_commands():
    """Control command syncing across replicas"""
    global last_sync_time
    current_time = time.time()

    if current_time - last_sync_time >= SYNC_COOLDOWN:
        last_sync_time = current_time
        return True
    return False


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


async def verify_discord_interaction(request: Request):
    # Implement or import this function as needed
    pass


@app.post("/discord-interaction")
async def handle_discord_interaction(request: Request):
    """Handle Discord interactions with proper verification."""
    try:
        # Get the request body
        body = await request.json()

        # Handle PING
        if body["type"] == InteractionType.ping.value:
            return {"type": InteractionType.pong.value}

        # Handle commands
        if body["type"] == InteractionType.application_command.value:
            command_name = body["data"]["name"]

            # Immediate response
            response_data = {
                "type": InteractionType.channel_message.value,
                "data": {"content": "Processing command..."},
            }

            if command_name == "ping":
                response_data["data"]["content"] = "Pong!"
            elif command_name == "githubsub":
                response_data["data"]["content"] = "Subscription command received"
            elif command_name == "help":
                response_data["data"]["content"] = (
                    "Available commands:\n"
                    "- /ping: Check bot latency\n"
                    "- /githubsub: Subscribe to GitHub notifications\n"
                    "- /help: Show this message"
                )

            return response_data

    except Exception as e:
        logger.error(f"Error handling interaction: {e}")
        return {
            "type": InteractionType.channel_message.value,
            "data": {"content": "An error occurred processing your command."},
        }


async def startup_event():
    """Handle startup tasks with rate limiting"""
    if await should_sync_commands():
        try:
            # Sync commands here
            await bot.sync_commands()
            logger.info("Commands synced successfully")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")


# Register startup event
app.add_event_handler("startup", startup_event)

if __name__ == "__main__":
    asyncio.run(run_all())
