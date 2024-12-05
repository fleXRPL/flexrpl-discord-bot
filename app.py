from fastapi import FastAPI, Request, Response
from nacl.signing import VerifyKey
import json
import logging
from config import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI with minimal settings
app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# Initialize the verify key once
verify_key = VerifyKey(bytes.fromhex(config.DISCORD_PUBLIC_KEY))

@app.post("/discord-interaction")
async def discord_interaction(request: Request):
    """Handle Discord interactions with minimal processing."""
    try:
        # Get signature (fast fail)
        signature = request.headers.get('X-Signature-Ed25519')
        timestamp = request.headers.get('X-Signature-Timestamp')
        
        if not signature or not timestamp:
            return Response(
                content='{"error":"invalid request"}',
                media_type="application/json",
                status_code=401
            )
        
        # Read body
        body = await request.body()
        
        # Verify the request
        try:
            verify_key.verify(
                (timestamp + body.decode()).encode(),
                bytes.fromhex(signature)
            )
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return Response(
                content='{"error":"invalid signature"}',
                media_type="application/json",
                status_code=401
            )
        
        # Handle PING
        if b'"type":1' in body:
            return Response(
                content='{"type":1}',
                media_type="application/json"
            )
        
        # Parse the request body for other interaction types
        try:
            request_data = json.loads(body)
            # Handle other interaction types here
            return Response(
                content='{"type":1}',
                media_type="application/json"
            )
        except json.JSONDecodeError:
            return Response(
                content='{"error":"invalid json"}',
                media_type="application/json",
                status_code=400
            )
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return Response(
            content='{"error":"internal error"}',
            media_type="application/json",
            status_code=500
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
