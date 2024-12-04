import asyncio
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from discord.ext import commands
from src.bot.events import setup_events
from src.bot.commands import setup_commands
from src.handlers.github_webhook import router as github_router
from config import config, ConfigValidationError
import os
from dotenv import load_dotenv
import nacl.signing
import nacl.exceptions
from fastapi import HTTPException
import discord
from fastapi.middleware.cors import CORSMiddleware
import json

load_dotenv()

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Discord Bot API",
    description="Discord bot for GitHub notifications",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# Add CORS middleware if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["X-Signature-Ed25519", "X-Signature-Timestamp"],
)

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = False
intents.typing = False
intents.dm_typing = False
intents.dm_reactions = False
intents.invites = False

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    application_id=int(config.DISCORD_APPLICATION_ID)
)

def verify_intents(intents: discord.Intents) -> None:
    """Verify that required intents are enabled."""
    required_intents = {
        'message_content': 'MESSAGE CONTENT INTENT',
        'members': 'SERVER MEMBERS INTENT'
    }
    
    missing_intents = []
    for intent_name, portal_name in required_intents.items():
        if not getattr(intents, intent_name):
            missing_intents.append(portal_name)
    
    if missing_intents:
        raise ConfigValidationError(
            f"Missing required privileged intents: {', '.join(missing_intents)}. "
            "Please enable them in Discord Developer Portal > Bot settings."
        )

# Initialize the verify key once at startup
verify_key = None
try:
    verify_key = nacl.signing.VerifyKey(bytes.fromhex(config.DISCORD_PUBLIC_KEY))
except Exception as e:
    logger.error(f"Failed to initialize Discord verify key: {e}")

@app.get("/")
async def health_check():
    """Health check endpoint for Railway"""
    return JSONResponse(
        content={
            "status": "healthy",
            "message": "Discord bot is running"
        },
        status_code=200
    )

@app.post("/discord-interaction")
async def discord_interaction(request: Request):
    """Handle Discord interactions with minimal overhead."""
    try:
        # Get headers immediately
        signature = request.headers.get('X-Signature-Ed25519')
        timestamp = request.headers.get('X-Signature-Timestamp')
        
        if not signature or not timestamp:
            return Response(
                content=json.dumps({"error": "missing signature"}),
                status_code=401
            )
        
        # Read body as bytes
        body = await request.body()
        body_str = body.decode()
        
        # Verify signature (fast fail)
        try:
            verify_key.verify(
                f"{timestamp}{body_str}".encode(),
                bytes.fromhex(signature)
            )
        except:
            return Response(
                content=json.dumps({"error": "invalid signature"}),
                status_code=401
            )
        
        # Parse interaction type (minimal JSON parsing)
        try:
            interaction_type = json.loads(body_str).get("type", 0)
            
            # Immediate response for PING
            if interaction_type == 1:
                return Response(
                    content=json.dumps({"type": 1}),
                    media_type="application/json"
                )
                
            # Quick response for other types
            return Response(
                content=json.dumps({
                    "type": 4,
                    "data": {"content": "Command received!"}
                }),
                media_type="application/json"
            )
            
        except json.JSONDecodeError:
            return Response(
                content=json.dumps({"error": "invalid request body"}),
                status_code=400
            )
            
    except Exception as e:
        logger.error(f"Interaction error: {e}")
        return Response(
            content=json.dumps({"error": "internal error"}),
            status_code=500
        )

@app.on_event("startup")
async def startup_event():
    """Initialize bot and start it in the background."""
    try:
        # Validate configuration first
        logger.info("Validating configuration...")
        config.validate()
        
        # Verify intents
        logger.info("Verifying Discord intents...")
        verify_intents(bot.intents)
        
        # Setup bot events and commands
        logger.info("Setting up bot events...")
        setup_events(bot)
        
        # Start bot first
        logger.info("Starting bot...")
        await bot.start(config.DISCORD_BOT_TOKEN)
        
        # Wait for bot to be ready
        logger.info("Waiting for bot to be ready...")
        while not bot.is_ready():
            await asyncio.sleep(0.1)
            
        # Now setup commands
        logger.info("Setting up bot commands...")
        await setup_commands(bot)
        
        logger.info("Bot started successfully")
        
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        raise

# Include routers
app.include_router(github_router, prefix="/webhook", tags=["webhooks"])

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    ) 