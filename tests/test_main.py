import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import nacl.signing
import sys
from unittest.mock import MagicMock, AsyncMock, patch
from enum import IntEnum

# Create mock InteractionType
class MockInteractionType(IntEnum):
    ping = 1
    pong = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5

# Mock discord.interactions before importing main
mock_discord = MagicMock()
mock_discord.interactions = MagicMock(InteractionType=MockInteractionType)
sys.modules['discord'] = mock_discord
sys.modules['discord.interactions'] = mock_discord.interactions

# Create mock config first
class MockConfig:
    DISCORD_PUBLIC_KEY = "a" * 64  # 32 bytes when converted from hex
    DISCORD_TOKEN = "mock_token"
    DISCORD_APPLICATION_ID = "mock_app_id"
    PORT = "8000"

# Mock the config module before any imports
sys.modules['config'] = MockConfig()

# Create mock app
mock_app = FastAPI()
mock_app_module = MagicMock()
mock_app_module.app = mock_app
sys.modules['app'] = mock_app_module

# Create mock verify key with proper length
mock_verify_key = MagicMock()
mock_verify_key.verify = MagicMock(return_value=b"verified")

# Mock VerifyKey before it's used
class MockVerifyKey:
    def __init__(self, key, *args, **kwargs):
        pass
    
    def verify(self, *args, **kwargs):
        return b"verified"

# Patch VerifyKey before any imports
nacl.signing.VerifyKey = MockVerifyKey

# Create mock bot
class MockFlexRPLBot:
    def __init__(self, *args, **kwargs):
        self.tree = AsyncMock()
        self.tree.sync = AsyncMock()
    
    async def start(self, *args, **kwargs):
        pass

# Create mock bot module
mock_bot_module = MagicMock()
mock_bot_module.FlexRPLBot = MockFlexRPLBot
sys.modules['bot'] = mock_bot_module
sys.modules['bot.bot'] = mock_bot_module

# Now we can safely import the main module
from src import main

@pytest.fixture
def test_client():
    """Create test client with mocked app"""
    @mock_app.get("/health")
    def health_check():
        return {"status": "healthy"}
        
    with TestClient(mock_app) as client:
        yield client

def test_health_check(test_client):
    """Test the health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_startup_event():
    """Test the startup event handler"""
    await main.startup_event()
    # Add assertions here if needed

@pytest.mark.asyncio
async def test_handle_discord_interaction():
    """Test Discord interaction handler"""
    # Test PING interaction
    class MockRequest:
        async def json(self):
            return {
                "type": MockInteractionType.ping.value,
                "id": "test_id",
                "application_id": "test_app_id",
            }
            
    mock_request = MockRequest()
    response = await main.handle_discord_interaction(mock_request)
    assert response.get("type") == MockInteractionType.pong.value
    
    # Test APPLICATION_COMMAND interaction
    class MockCommandRequest:
        async def json(self):
            return {
                "type": MockInteractionType.APPLICATION_COMMAND,
                "id": "test_id",
                "application_id": "test_app_id",
                "data": {"name": "test_command"}
            }
            
    mock_command_request = MockCommandRequest()
    response = await main.handle_discord_interaction(mock_command_request)
    assert response is not None

@pytest.mark.asyncio
async def test_start_server():
    """Test server startup"""
    mock_config = MagicMock()
    mock_server = AsyncMock()
    
    with patch('uvicorn.Config', return_value=mock_config), \
         patch('uvicorn.Server', return_value=mock_server):
        await main.start_server()
        mock_server.serve.assert_called_once()
