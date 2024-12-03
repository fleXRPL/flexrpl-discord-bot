from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.security import HTTPBearer
from src.utils.formatting import format_github_event
import hmac
import hashlib
from config import config

router = APIRouter()
security = HTTPBearer()

async def verify_signature(request: Request):
    """Verify GitHub webhook signature."""
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(status_code=400, detail="No signature header")

    body = await request.body()
    hmac_gen = hmac.new(
        config.GITHUB_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    )
    expected_signature = f"sha256={hmac_gen.hexdigest()}"

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

@router.post("/github")
async def github_webhook(
    request: Request,
    _: HTTPBearer = Depends(security)
):
    """Handle GitHub webhook events."""
    await verify_signature(request)
    event_type = request.headers.get("X-GitHub-Event")
    payload = await request.json()
    
    formatted_message = format_github_event(event_type, payload)
    # TODO: Send formatted message to Discord channel
    
    return {"status": "success"} 