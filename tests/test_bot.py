import pytest
from discord.ext import commands
import os
from unittest.mock import patch, AsyncMock, MagicMock, PropertyMock, call
from src.bot.bot import FlexRPLBot
from discord import app_commands

@pytest.fixture
async def bot():
    """Create a bot instance for testing."""
    with patch('src.bot.bot.setup_commands') as mock_setup_commands, \
         patch('src.bot.bot.setup_events') as mock_setup_events:
        bot = FlexRPLBot()
        # Mock the connection state
        bot._connection = AsyncMock()
        bot._connection.is_ready = lambda: True
        mock_setup_commands.return_value = AsyncMock()
        
        # Mock the close method to prevent errors
        bot.close = AsyncMock()
        
        yield bot
        await bot.close()

@pytest.mark.asyncio
async def test_bot_initialization():
    """Test bot initialization."""
    bot = FlexRPLBot()
    
    assert isinstance(bot, commands.Bot)
    assert bot.command_prefix == "!"
    assert bot.intents.message_content is True
    assert bot.intents.guilds is True

@pytest.mark.asyncio
async def test_setup_hook_success(bot):
    """Test successful setup hook execution."""
    # Create async mocks for both functions
    setup_events_mock = AsyncMock()
    setup_commands_mock = AsyncMock()
    
    # Patch both functions at the module level
    with patch('src.bot.bot.setup_events', setup_events_mock), \
         patch('src.bot.bot.setup_commands', setup_commands_mock), \
         patch.object(bot.tree, 'sync', new_callable=AsyncMock) as sync_mock:
        
        # Execute the hook
        await bot.setup_hook()
        
        # Verify all mocks were called correctly
        setup_events_mock.assert_called_once_with(bot)
        setup_commands_mock.assert_called_once_with(bot)
        sync_mock.assert_called_once()

@pytest.mark.asyncio
async def test_setup_hook_failure(bot):
    """Test setup hook failure."""
    with patch.object(bot.tree, 'sync', side_effect=Exception("Test error")), \
         pytest.raises(Exception):
        await bot.setup_hook()

@pytest.mark.asyncio
async def test_on_ready(bot):
    """Test on_ready event handler."""
    # Mock bot user using property setter
    user_mock = MagicMock()
    user_mock.name = "TestBot"
    user_mock.id = "123456789"
    with patch.object(FlexRPLBot, 'user', new_callable=PropertyMock) as mock_user:
        mock_user.return_value = user_mock
        
        # Mock tree commands
        mock_cmd = MagicMock()
        mock_cmd.name = "test"
        mock_cmd.description = "Test command"
        bot.tree.get_commands = MagicMock(return_value=[mock_cmd])
        
        await bot.on_ready()
        bot.tree.get_commands.assert_called_once()

@pytest.mark.asyncio
async def test_on_app_command_error_cooldown(bot):
    """Test command cooldown error handling."""
    # Create a more complete interaction mock structure
    response_mock = AsyncMock()
    response_mock.is_done = MagicMock(return_value=False)
    response_mock.defer = AsyncMock()
    
    followup_mock = AsyncMock()
    
    interaction = AsyncMock()
    interaction.response = response_mock
    interaction.followup = followup_mock
    
    error = MagicMock(spec=app_commands.CommandOnCooldown)
    error.retry_after = 5.0
    
    # Call the error handler
    await bot.on_app_command_error(interaction, error)
    
    # Verify the calls
    assert response_mock.is_done.call_count == 1
    assert response_mock.defer.call_count == 1
    assert response_mock.defer.call_args == call(ephemeral=True)
    assert followup_mock.send.call_count == 1
    assert "cooldown" in followup_mock.send.call_args.args[0]
    assert "5.0" in followup_mock.send.call_args.args[0]

@pytest.mark.asyncio
async def test_on_app_command_error_missing_permissions(bot):
    """Test missing permissions error handling."""
    # Create a more complete interaction mock structure
    response_mock = AsyncMock()
    response_mock.is_done = MagicMock(return_value=False)
    response_mock.defer = AsyncMock()
    
    followup_mock = AsyncMock()
    
    interaction = AsyncMock()
    interaction.response = response_mock
    interaction.followup = followup_mock
    
    error = MagicMock(spec=app_commands.MissingPermissions)
    
    # Call the error handler
    await bot.on_app_command_error(interaction, error)
    
    # Verify the calls
    assert response_mock.is_done.call_count == 1
    assert response_mock.defer.call_count == 1
    assert response_mock.defer.call_args == call(ephemeral=True)
    assert followup_mock.send.call_args == call(
        "You don't have permission to use this command.",
        ephemeral=True
    )

@pytest.mark.asyncio
async def test_on_app_command_error_generic(bot):
    """Test generic error handling."""
    # Create a more complete interaction mock structure
    response_mock = AsyncMock()
    response_mock.is_done = MagicMock(return_value=False)
    response_mock.defer = AsyncMock()
    
    followup_mock = AsyncMock()
    
    interaction = AsyncMock()
    interaction.response = response_mock
    interaction.followup = followup_mock
    
    error = Exception("Test error")
    
    # Call the error handler
    await bot.on_app_command_error(interaction, error)
    
    # Verify the calls
    assert response_mock.is_done.call_count == 1
    assert response_mock.defer.call_count == 1
    assert response_mock.defer.call_args == call(ephemeral=True)
    assert followup_mock.send.call_args == call(
        "An error occurred while processing the command.",
        ephemeral=True
    )

@pytest.mark.asyncio
async def test_on_app_command_error_response_already_done(bot):
    """Test error handling when response is already done."""
    # Create a more complete interaction mock structure
    response_mock = AsyncMock()
    response_mock.is_done = MagicMock(return_value=True)
    response_mock.defer = AsyncMock()
    
    followup_mock = AsyncMock()
    
    interaction = AsyncMock()
    interaction.response = response_mock
    interaction.followup = followup_mock
    
    error = Exception("Test error")
    
    await bot.on_app_command_error(interaction, error)
    
    assert response_mock.defer.call_count == 0
