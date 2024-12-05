import asyncio
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from discord import Interaction
from discord.interactions import InteractionType
from discord.webhook.async_ import async_context
import json

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


@app.post("/discord-interaction")
async def handle_discord_interaction(request: Request):
    """Handle Discord interactions with proper verification."""
    try:
        # Get the request body as bytes for signature verification
        body = await request.body()

        # Get Discord headers
        signature = request.headers.get('X-Signature-Ed25519')
        timestamp = request.headers.get('X-Signature-Timestamp')

        # Verify the interaction
        interaction_data = json.loads(body)
        interaction = Interaction(data=interaction_data, state=bot._connection)

        # Handle different interaction types
        if interaction.type == InteractionType.ping:
            return {"type": 1}  # Pong response

        elif interaction.type == InteractionType.application_command:
            # Set up async context for the interaction
            async with async_context():
                command = bot.tree.get_command(interaction.data["name"])
                if command:
                    await command.callback(interaction)
                    return {"type": 5}  # Deferred response

        return {"type": 4, "data": {"content": "Unknown command"}}

    except Exception as e:
        logger.error(f"Error handling Discord interaction: {e}")
        return {"type": 4, "data": {"content": "An error occurred"}}


if __name__ == "__main__":
    asyncio.run(run_all())
