import json
import logging
import math

from discord import InteractionType
from fastapi import APIRouter, Request, Response
from nacl.exceptions import ValueError as NaclValueError
from nacl.signing import VerifyKey

from config import config
from src.bot.bot import bot

router = APIRouter()
logger = logging.getLogger(__name__)

RESPONSE_TYPES = {
    "PONG": 1,
    "CHANNEL_MESSAGE": 4,
    "DEFERRED_CHANNEL_MESSAGE": 5,
    "DEFERRED_UPDATE_MESSAGE": 6,
    "UPDATE_MESSAGE": 7,
    "APPLICATION_COMMAND_AUTOCOMPLETE_RESULT": 8,
    "MODAL": 9,
    "PREMIUM_REQUIRED": 10,
}


def get_verify_key():
    """Get the Discord verification key."""
    try:
        return VerifyKey(bytes.fromhex(config.DISCORD_PUBLIC_KEY))
    except (ValueError, NaclValueError) as e:
        logger.error(f"Invalid Discord public key: {e}")
        return None


@router.post("/discord-interaction")
async def discord_interaction(request: Request) -> Response:
    """Handle Discord interactions."""
    try:
        # Verify the request
        verify_key = get_verify_key()
        signature = request.headers.get("X-Signature-Ed25519")
        timestamp = request.headers.get("X-Signature-Timestamp")

        if not verify_key or not signature or not timestamp:
            logger.error("Missing verification requirements")
            return Response(status_code=401)

        body = await request.body()
        body_str = body.decode()

        try:
            verify_key.verify(
                f"{timestamp}{body_str}".encode(), bytes.fromhex(signature)
            )
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return Response(status_code=401)

        # Parse and handle the interaction
        interaction_data = json.loads(body_str)
        interaction_type = interaction_data.get("type")

        logger.info("Received Discord interaction")
        logger.info(f"Processing interaction type: {interaction_type}")

        # Handle PING
        if interaction_type == InteractionType.ping.value:
            logger.info("Handling PING interaction")
            return Response(content='{"type":1}', media_type="application/json")

        # Handle APPLICATION_COMMAND
        if interaction_type == InteractionType.application_command.value:
            command_name = interaction_data.get("data", {}).get("name")
            logger.info(f"Handling command: {command_name}")

            if command_name == "ping":
                try:
                    latency = (
                        round(bot.latency * 1000) if not math.isnan(bot.latency) else 0
                    )
                    message = f"Pong! 🏓 (Latency: {latency}ms)"
                except (ValueError, TypeError):
                    message = "Pong! 🏓 (Latency unavailable)"

                return Response(
                    content=json.dumps(
                        {
                            "type": RESPONSE_TYPES["CHANNEL_MESSAGE"],
                            "data": {"content": message, "flags": 64},
                        }
                    ),
                    media_type="application/json",
                )
            elif command_name == "help":
                try:
                    commands = list(bot.tree.get_commands())
                    logger.info(f"Found {len(commands)} commands")

                    # Fallback to bot's command list if tree is empty
                    if not commands:
                        commands = [
                            {"name": "ping", "description": "Check bot latency"},
                            {"name": "help", "description": "Show available commands"},
                            {
                                "name": "githubsub",
                                "description": "Subscribe to GitHub notifications",
                            },
                        ]

                    commands_list = [
                        f"`/{cmd['name']}` - {cmd['description']}" for cmd in commands
                    ]

                    return Response(
                        content=json.dumps(
                            {
                                "type": RESPONSE_TYPES["CHANNEL_MESSAGE"],
                                "data": {
                                    "content": "**Available Commands:**\n"
                                    + "\n".join(commands_list),
                                    "flags": 64,
                                },
                            }
                        ),
                        media_type="application/json",
                    )
                except Exception as e:
                    logger.error(f"Error getting commands: {e}")
                    return Response(
                        content=json.dumps(
                            {
                                "type": RESPONSE_TYPES["CHANNEL_MESSAGE"],
                                "data": {
                                    "content": "❌ Error retrieving commands.",
                                    "flags": 64,
                                },
                            }
                        ),
                        media_type="application/json",
                    )
            elif command_name == "githubsub":
                return Response(
                    content=json.dumps(
                        {
                            "type": RESPONSE_TYPES["DEFERRED_CHANNEL_MESSAGE"],
                            "data": {"flags": 64},  # Ephemeral flag
                        }
                    ),
                    media_type="application/json",
                )

        logger.warning(f"Unhandled interaction type: {interaction_type}")
        return Response(content='{"type":1}', media_type="application/json")

    except Exception as e:
        logger.error(f"Error processing interaction: {e}", exc_info=True)
        return Response(
            content=json.dumps(
                {
                    "type": 4,
                    "data": {
                        "content": "An error occurred while processing the command.",
                        "flags": 64,
                    },
                }
            ),
            media_type="application/json",
        )
