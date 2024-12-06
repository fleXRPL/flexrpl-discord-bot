import logging
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from discord.ext import commands
from discord import Guild
from src.bot.events import setup_events

@pytest.fixture
def mock_bot():
    """Create a mock bot instance."""
    bot = MagicMock(spec=commands.Bot)
    # Store event handlers
    bot.event_handlers = {}
    
    # Mock the event decorator
    def event(coro):
        bot.event_handlers[coro.__name__] = coro
        return coro
    bot.event = event
    
    return bot

@pytest.fixture
def mock_guild():
    """Create a mock guild instance."""
    guild = MagicMock(spec=Guild)
    guild.name = "Test Guild"
    guild.id = 123456789
    return guild

@pytest.fixture
def mock_ctx():
    """Create a mock context."""
    ctx = MagicMock()
    ctx.send = AsyncMock()
    return ctx

def test_setup_events(mock_bot):
    """Test that events are properly registered."""
    setup_events(mock_bot)
    
    # Verify that all expected events are registered
    assert 'on_guild_join' in mock_bot.event_handlers
    assert 'on_guild_remove' in mock_bot.event_handlers
    assert 'on_command_error' in mock_bot.event_handlers

@pytest.mark.asyncio
async def test_on_guild_join(mock_bot, mock_guild, caplog):
    """Test the guild join event handler."""
    with caplog.at_level(logging.INFO):
        setup_events(mock_bot)
        await mock_bot.event_handlers['on_guild_join'](mock_guild)
        
        assert f"Bot has been added to guild: {mock_guild.name} (ID: {mock_guild.id})" in caplog.text

@pytest.mark.asyncio
async def test_on_guild_remove(mock_bot, mock_guild, caplog):
    """Test the guild remove event handler."""
    with caplog.at_level(logging.INFO):
        setup_events(mock_bot)
        await mock_bot.event_handlers['on_guild_remove'](mock_guild)
        
        assert f"Bot has been removed from guild: {mock_guild.name} (ID: {mock_guild.id})" in caplog.text

@pytest.mark.asyncio
async def test_on_command_error_command_not_found(mock_bot, mock_ctx):
    """Test command not found error handling."""
    setup_events(mock_bot)
    error = commands.CommandNotFound()
    
    await mock_bot.event_handlers['on_command_error'](mock_ctx, error)
    mock_ctx.send.assert_not_called()

@pytest.mark.asyncio
async def test_on_command_error_generic(mock_bot, mock_ctx, caplog):
    """Test generic command error handling."""
    with caplog.at_level(logging.ERROR):
        setup_events(mock_bot)
        error = Exception("Test error")
        
        await mock_bot.event_handlers['on_command_error'](mock_ctx, error)
        
        mock_ctx.send.assert_called_once_with("An error occurred: Test error")
        assert "Command error: Test error" in caplog.text
