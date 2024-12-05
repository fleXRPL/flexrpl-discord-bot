import hashlib
import hmac
import logging

import aiohttp
from discord import AsyncWebhookAdapter, Webhook
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer

from config import config
from src.utils.formatting import format_github_event

router = APIRouter()
security = HTTPBearer()

logger = logging.getLogger(__name__)


async def verify_signature(request: Request):
    """Verify GitHub webhook signature."""
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(status_code=400, detail="No signature header")

    body = await request.body()
    hmac_gen = hmac.new(config.GITHUB_WEBHOOK_SECRET.encode(), body, hashlib.sha256)
    expected_signature = f"sha256={hmac_gen.hexdigest()}"

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")


async def send_discord_webhook(webhook_url: str, content: str):
    """Send a message to Discord via webhook."""
    try:
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(
                webhook_url, adapter=AsyncWebhookAdapter(session)
            )
            await webhook.send(content=content)
            logger.info("Successfully sent webhook message to Discord")
    except Exception as e:
        logger.error(f"Error sending webhook to Discord: {e}")
        raise HTTPException(status_code=500, detail="Failed to send webhook to Discord")


async def handle_github_webhook(event_type: str, payload: dict):
    """Handle incoming GitHub webhook events."""
    try:
        # TODO: Implement webhook URL configuration and sending
        logger.info(f"Processed GitHub webhook event: {event_type}")
        return format_github_event(event_type, payload)
    except Exception as e:
        logger.error(f"Error processing GitHub webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process GitHub webhook")


@router.post("/github")
async def github_webhook(request: Request, _: HTTPBearer = Depends(security)):
    """Handle GitHub webhook events."""
    await verify_signature(request)
    event_type = request.headers.get("X-GitHub-Event")
    payload = await request.json()

    await handle_github_webhook(event_type, payload)
    # TODO: Send formatted message to Discord channel

    return {"status": "success"}
