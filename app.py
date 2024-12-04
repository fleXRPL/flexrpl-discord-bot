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
import uvicorn
import uvloop
import time

load_dotenv()

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Initialize FastAPI app
app = FastAPI(
    title="Discord Bot API",
    description="Discord bot for GitHub notifications",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    default_response_class=Response  # Faster response handling
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
        # Quick headers check
        signature = request.headers.get('X-Signature-Ed25519')
        timestamp = request.headers.get('X-Signature-Timestamp')
        
        if not signature or not timestamp:
            return Response(
                content='{"error":"invalid signature"}',
                media_type="application/json",
                status_code=401
            )
        
        # Fast body read
        body = await request.body()
        
        # Immediate PING response if possible
        try:
            if b'"type":1' in body:  # Quick check without full JSON parsing
                return Response(
                    content='{"type":1}',
                    media_type="application/json"
                )
        except:
            pass
        
        # Continue with normal verification if not a PING
        # ... rest of the verification code ...
        
    except Exception as e:
        logger.error(f"Interaction error: {e}")
        return Response(
            content='{"error":"internal error"}',
            media_type="application/json",
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

# Add timing middleware
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    ) 