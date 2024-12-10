import json
import logging
import math

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
async def discord_interaction(request: Request):
    """Handle Discord interactions with minimal processing."""
    try:
        # Get signature (fast fail)
        signature = request.headers.get("X-Signature-Ed25519")
        timestamp = request.headers.get("X-Signature-Timestamp")

        logger.info("Received Discord interaction")
        logger.debug(f"Headers: {request.headers}")

        if not signature or not timestamp:
            logger.warning("Missing signature or timestamp")
            return Response(
                content='{"error":"invalid request"}',
                media_type="application/json",
                status_code=401,
            )

        # Read body
        body = await request.body()
        request_data = json.loads(body)
        logger.debug(f"Request data: {request_data}")

        # Verify the request
        verify_key = get_verify_key()
        if not verify_key:
            logger.error("Failed to get verify key")
            return Response(
                content='{"error":"configuration error"}',
                media_type="application/json",
                status_code=500,
            )

        try:
            verify_key.verify(
                (timestamp + body.decode()).encode(), bytes.fromhex(signature)
            )
            logger.debug("Signature verification successful")
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return Response(
                content='{"error":"invalid signature"}',
                media_type="application/json",
                status_code=401,
            )

        interaction_type = request_data.get("type")
        logger.info(f"Processing interaction type: {interaction_type}")

        # Handle PING
        if interaction_type == 1:
            logger.info("Handling PING interaction")
            return Response(content='{"type":1}', media_type="application/json")

        # Handle APPLICATION_COMMAND
        if interaction_type == 2:
            response_data = await handle_command(request_data)
            return Response(
                content=json.dumps(response_data), media_type="application/json"
            )

        # Default response
        logger.warning(f"Unhandled interaction type: {interaction_type}")
        return Response(content='{"type":1}', media_type="application/json")

    except Exception as e:
        logger.error(f"Error processing interaction: {e}", exc_info=True)
        return Response(
            content='{"error":"internal error"}',
            media_type="application/json",
            status_code=500,
        )


async def handle_command(interaction_data: dict) -> dict:
    """Handle Discord command interactions."""
    try:
        command_name = interaction_data.get("data", {}).get("name")
        logger.info(f"Handling command: {command_name}")

        # Handle different commands
        if command_name == "ping":
            try:
                # Check if latency is valid
                latency = bot.latency
                if latency and not math.isnan(latency):
                    latency_ms = round(latency * 1000)
                    return {
                        "type": 4,
                        "data": {"content": f"Pong! 🏓 ({latency_ms}ms)", "flags": 64},
                    }
                else:
                    return {
                        "type": 4,
                        "data": {
                            "content": "Pong! 🏓 (Latency unavailable)",
                            "flags": 64,
                        },
                    }
            except Exception as e:
                logger.error(f"Error in ping command: {e}", exc_info=True)
                return {
                    "type": 4,
                    "data": {
                        "content": "❌ Could not get latency information.",
                        "flags": 64,
                    },
                }
        elif command_name == "help":
            try:
                # Get list of commands
                commands = list(bot.tree.get_commands())
                logger.info(f"Found {len(commands)} commands")

                if not commands:
                    logger.warning("No commands found in bot.tree")
                    return {
                        "type": 4,
                        "data": {
                            "content": "❌ No commands are currently available.",
                            "flags": 64,
                        },
                    }

                # Build commands list with logging
                commands_list = []
                for cmd in commands:
                    command_info = f"`/{cmd.name}` - {cmd.description}"
                    logger.debug(f"Adding command to help: {command_info}")
                    commands_list.append(command_info)

                content = "**Available Commands:**\n" + "\n".join(commands_list)
                logger.info(f"Sending help content with {len(commands_list)} commands")
                logger.debug(f"Full help content: {content}")

                return {"type": 4, "data": {"content": content, "flags": 64}}
            except AttributeError as e:
                logger.error(f"Bot tree access error: {e}", exc_info=True)
                return {
                    "type": 4,
                    "data": {
                        "content": "❌ Could not access commands list.",
                        "flags": 64,
                    },
                }
            except Exception as e:
                logger.error(f"Error generating help content: {e}", exc_info=True)
                return {
                    "type": 4,
                    "data": {
                        "content": (
                            "❌ An error occurred while retrieving commands list."
                        ),
                        "flags": 64,
                    },
                }
        elif command_name == "githubsub":
            # Only defer long-running commands
            logger.info("Sending deferred response")
            return {
                "type": 5,  # DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
                "data": {"flags": 64},  # EPHEMERAL
            }

        # Default response for unknown commands
        return {"type": 4, "data": {"content": "Unknown command", "flags": 64}}

    except Exception as e:
        logger.error(f"Error handling command: {e}", exc_info=True)
        return {
            "type": 4,
            "data": {
                "content": "❌ An error occurred while processing the command.",
                "flags": 64,
            },
        }
