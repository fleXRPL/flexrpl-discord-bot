import logging
import pytest
from unittest.mock import AsyncMock, MagicMock
from discord.ext import commands
from src.bot.events import setup_events

@pytest.fixture
def mock_bot():
    """Create a mock bot instance."""
    bot = MagicMock(spec=commands.Bot)
    # Mock the event decorator to store handlers
    bot.event_handlers = {}
    def event_decorator(func):
        bot.event_handlers[func.__name__] = func
        return func
    bot.event = event_decorator
    return bot

@pytest.mark.asyncio
async def test_setup_events(mock_bot):
    """Test that events are properly registered."""
    await setup_events(mock_bot)
    assert 'on_guild_join' in mock_bot.event_handlers
    assert 'on_guild_remove' in mock_bot.event_handlers
    assert 'on_command_error' in mock_bot.event_handlers

@pytest.mark.asyncio
async def test_on_guild_join(mock_bot, caplog):
    """Test the guild join event handler."""
    mock_guild = MagicMock()
    mock_guild.name = "Test Guild"
    mock_guild.id = "123456"
    
    with caplog.at_level(logging.INFO):
        await setup_events(mock_bot)
        await mock_bot.event_handlers['on_guild_join'](mock_guild)
        assert "Bot has been added to guild: Test Guild" in caplog.text

@pytest.mark.asyncio
async def test_on_guild_remove(mock_bot, caplog):
    """Test the guild remove event handler."""
    mock_guild = MagicMock()
    mock_guild.name = "Test Guild"
    mock_guild.id = "123456"
    
    with caplog.at_level(logging.INFO):
        await setup_events(mock_bot)
        await mock_bot.event_handlers['on_guild_remove'](mock_guild)
        assert "Bot has been removed from guild: Test Guild" in caplog.text

@pytest.mark.asyncio
async def test_on_command_error_command_not_found(mock_bot):
    """Test command not found error handling."""
    mock_ctx = AsyncMock()
    await setup_events(mock_bot)
    error = commands.CommandNotFound()
    await mock_bot.event_handlers['on_command_error'](mock_ctx, error)
    mock_ctx.send.assert_not_called()

@pytest.mark.asyncio
async def test_on_command_error_generic(mock_bot, caplog):
    """Test generic command error handling."""
    mock_ctx = AsyncMock()
    with caplog.at_level(logging.ERROR):
        await setup_events(mock_bot)
        error = Exception("Test error")
        await mock_bot.event_handlers['on_command_error'](mock_ctx, error)
        assert "Command error: Test error" in caplog.text
        mock_ctx.send.assert_called_once_with("An error occurred: Test error")
