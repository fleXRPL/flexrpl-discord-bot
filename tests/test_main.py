import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import discord
from discord.interactions import InteractionType
import time
import os
import asyncio
import sys

# Mock the bot module before importing main
mock_bot = MagicMock()
mock_flexrpl = MagicMock()
sys.modules['bot'] = mock_bot
sys.modules['bot.bot'] = MagicMock(FlexRPLBot=mock_flexrpl)

from src.main import (
    app, should_sync_commands, start_bot, start_server, 
    handle_discord_interaction, startup_event
)

# Setup test client
client = TestClient(app)

@pytest.fixture
def mock_bot_instance():
    """Create a mock bot instance for testing."""
    mock = MagicMock()
    mock.tree = MagicMock()
    mock.tree.sync = AsyncMock()
    mock.start = AsyncMock()
    return mock

def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Discord bot is running"}

def test_test_endpoint():
    """Test test endpoint."""
    response = client.get("/test")
    assert response.status_code == 200
    assert "commands" in response.json()
    assert "/ping" in response.json()["commands"]

@pytest.mark.asyncio
async def test_should_sync_commands():
    """Test command sync rate limiting."""
    assert await should_sync_commands() is True
    assert await should_sync_commands() is False

@pytest.mark.asyncio
async def test_handle_discord_interaction_ping():
    """Test handling PING interaction."""
    with patch('src.main.InteractionType') as mock_interaction_type:
        # Mock the interaction type values
        mock_interaction_type.ping.value = 1
        mock_interaction_type.pong.value = 1
        
        mock_request = MagicMock(
            json=AsyncMock(return_value={"type": mock_interaction_type.ping.value})
        )
        
        response = await handle_discord_interaction(mock_request)
        assert response["type"] == mock_interaction_type.pong.value

@pytest.mark.asyncio
async def test_handle_discord_interaction_command():
    """Test handling command interaction."""
    mock_request = MagicMock(
        json=AsyncMock(return_value={
            "type": 2,  # APPLICATION_COMMAND type
            "data": {"name": "ping"}
        })
    )
    response = await handle_discord_interaction(mock_request)
    assert response["type"] == 4
    assert response["data"]["content"] == "Pong!"

@pytest.mark.asyncio
async def test_handle_discord_interaction_help():
    """Test handling help command."""
    mock_request = MagicMock(
        json=AsyncMock(return_value={
            "type": 2,
            "data": {"name": "help"}
        })
    )
    response = await handle_discord_interaction(mock_request)
    assert "Available commands" in response["data"]["content"]

@pytest.mark.asyncio
async def test_handle_discord_interaction_error():
    """Test handling interaction error."""
    mock_request = MagicMock(
        json=AsyncMock(side_effect=Exception("Test error"))
    )
    response = await handle_discord_interaction(mock_request)
    assert "An error occurred" in response["data"]["content"]

@pytest.mark.asyncio
async def test_startup_event(mock_bot_instance):
    """Test startup event handler."""
    with patch('src.main.bot', mock_bot_instance), \
         patch('src.main.should_sync_commands', AsyncMock(return_value=True)), \
         patch('src.main.asyncio.sleep', AsyncMock()):
        await startup_event()
        mock_bot_instance.tree.sync.assert_called_once() 