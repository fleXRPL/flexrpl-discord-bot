import json
import logging

from discord import InteractionType
from fastapi import APIRouter, Request, Response
from nacl.exceptions import ValueError as NaclValueError
from nacl.signing import VerifyKey

from config import config
from src.bot.bot import bot

router = APIRouter()
logger = logging.getLogger(__name__)


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

        if not signature or not timestamp:
            return Response(status_code=401)

        body = await request.body()
        try:
            verify_key.verify(
                f"{timestamp}{body.decode()}".encode(), bytes.fromhex(signature)
            )
        except (ValueError, NaclValueError):
            return Response(status_code=401)

        # Parse the request data
        request_data = json.loads(body)
        interaction_type = request_data.get("type")

        logger.info("Received Discord interaction")
        logger.info(f"Processing interaction type: {interaction_type}")

        # Handle PING
        if interaction_type == InteractionType.ping.value:
            logger.info("Handling PING interaction")
            return Response(content='{"type":1}', media_type="application/json")

        # Handle APPLICATION_COMMAND
        if interaction_type == InteractionType.application_command.value:
            command_name = request_data.get("data", {}).get("name")
            logger.info(f"Handling command: {command_name}")

            if command_name == "ping":
                latency = round(bot.latency * 1000)
                return Response(
                    content=json.dumps(
                        {
                            "type": 4,
                            "data": {
                                "content": f"Pong! 🏓 (Latency: {latency}ms)",
                                "flags": 64,
                            },
                        }
                    ),
                    media_type="application/json",
                )
            elif command_name == "help":
                commands = bot.tree.get_commands()
                logger.info(f"Found {len(commands)} commands")
                if not commands:
                    logger.warning("No commands found in bot.tree")
                    return Response(
                        content=json.dumps(
                            {
                                "type": 4,
                                "data": {
                                    "content": "❌ No commands are currently available.",
                                    "flags": 64,
                                },
                            }
                        ),
                        media_type="application/json",
                    )

                commands_list = [
                    f"`/{cmd.name}` - {cmd.description}" for cmd in commands
                ]
                return Response(
                    content=json.dumps(
                        {
                            "type": 4,
                            "data": {
                                "content": "**Available Commands:**\n"
                                + "\n".join(commands_list),
                                "flags": 64,
                            },
                        }
                    ),
                    media_type="application/json",
                )
            elif command_name == "githubsub":
                return Response(
                    content=json.dumps(
                        {"type": 5, "data": {"flags": 64}}  # Deferred response
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
