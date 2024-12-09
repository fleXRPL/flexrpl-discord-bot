import json
import logging

from fastapi import APIRouter, Request, Response
from nacl.exceptions import ValueError as NaclValueError
from nacl.signing import VerifyKey

from config import config

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

        if not signature or not timestamp:
            return Response(
                content='{"error":"invalid request"}',
                media_type="application/json",
                status_code=401,
            )

        # Read body
        body = await request.body()

        # Verify the request
        verify_key = get_verify_key()
        if not verify_key:
            return Response(
                content='{"error":"configuration error"}',
                media_type="application/json",
                status_code=500,
            )

        try:
            verify_key.verify(
                (timestamp + body.decode()).encode(), bytes.fromhex(signature)
            )
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return Response(
                content='{"error":"invalid signature"}',
                media_type="application/json",
                status_code=401,
            )

        # Parse the request body
        request_data = json.loads(body)
        interaction_type = request_data.get("type")

        # Handle PING
        if interaction_type == 1:
            return Response(content='{"type":1}', media_type="application/json")

        # Handle APPLICATION_COMMAND
        if interaction_type == 2:
            # Return a deferred response immediately
            return Response(content='{"type":5}', media_type="application/json")

        # Default response
        return Response(content='{"type":1}', media_type="application/json")

    except Exception as e:
        logger.error(f"Error: {e}")
        return Response(
            content='{"error":"internal error"}',
            media_type="application/json",
            status_code=500,
        )