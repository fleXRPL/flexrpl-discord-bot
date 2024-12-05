import asyncio
import logging
import os

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
        # Verify the interaction first
        interaction = await verify_discord_interaction(request)

        # Immediately acknowledge the interaction
        await interaction.response.defer()

        # Then process the command
        if interaction.type == InteractionType.application_command:
            command_name = interaction.data["name"]

            if command_name == "ping":
                await interaction.followup.send("Pong!")
            elif command_name == "githubsub":
                await interaction.followup.send("Subscription command received")
            elif command_name == "help":
                await interaction.followup.send(
                    "Available commands:\n- /ping: Check bot latency\n"
                    "- /githubsub: Subscribe to GitHub notifications\n"
                    "- /help: Show this message"
                )

    except Exception as e:
        logger.error(f"Error handling interaction: {e}")
        return {"type": 1}

    return {"type": 1}


if __name__ == "__main__":
    asyncio.run(run_all())
