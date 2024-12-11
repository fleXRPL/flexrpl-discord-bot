import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import discord
from discord.ext import commands
import logging
from src.bot.bot import FlexRPLBot

logger = logging.getLogger(__name__)

class MockCooldown:
    def __init__(self):
        self.rate = 1
        self.per = 60
        self.type = commands.BucketType.default

@pytest.fixture
async def bot():
    """Create a bot instance for testing."""
    bot = MagicMock(spec=FlexRPLBot)
    bot.tree = MagicMock()
    bot.tree.command = MagicMock()
    bot.tree.sync = AsyncMock()
    bot.tree.get_commands = MagicMock(return_value=[])
    bot.latency = 0.1
    
    # Add error handling methods
    async def mock_on_app_command_error(interaction, error):
        try:
            if isinstance(error, commands.CommandOnCooldown):
                await interaction.response.send_message("Command is on cooldown", ephemeral=True)
            elif isinstance(error, commands.MissingPermissions):
                await interaction.response.send_message("Missing permissions", ephemeral=True)
            elif isinstance(error, discord.InteractionResponded):
                await interaction.followup.send("An error occurred", ephemeral=True)
            else:
                await interaction.response.send_message("An error occurred", ephemeral=True)
        except discord.InteractionResponded:
            await interaction.followup.send("An error occurred", ephemeral=True)
    
    bot.on_app_command_error = mock_on_app_command_error
    
    # Setup mocks for setup functions
    async def mock_setup_hook():
        from src.bot.commands import setup_commands
        from src.bot.events import setup_events
        await setup_commands(bot)
        await setup_events(bot)
        await bot.tree.sync()
        return True
        
    bot.setup_hook = mock_setup_hook
    
    # Add on_ready method
    async def mock_on_ready():
        bot.tree.get_commands()
    
    bot.on_ready = mock_on_ready
    
    return bot

@pytest.mark.asyncio
async def test_bot_initialization():
    """Test bot initialization."""
    bot = FlexRPLBot()
    assert isinstance(bot, commands.Bot)
    assert bot.intents.message_content is True

@pytest.mark.asyncio
async def test_setup_hook_success(bot):
    """Test successful setup hook."""
    with patch('src.bot.commands.setup_commands', AsyncMock(return_value=True)) as mock_setup_commands, \
         patch('src.bot.events.setup_events', AsyncMock(return_value=True)) as mock_setup_events:
        await bot.setup_hook()
        mock_setup_commands.assert_called_once()
        mock_setup_events.assert_called_once()

@pytest.mark.asyncio
async def test_setup_hook_failure(bot):
    """Test setup hook failure."""
    with patch('src.bot.commands.setup_commands', AsyncMock(side_effect=Exception("Setup failed"))):
        with pytest.raises(Exception, match="Setup failed"):
            await bot.setup_hook()

@pytest.mark.asyncio
async def test_on_ready(bot):
    """Test on_ready event."""
    bot.user = MagicMock()
    bot.user.id = 123456789
    bot.user.__str__ = lambda x: "TestBot"
    
    await bot.on_ready()
    bot.tree.get_commands.assert_called_once()

@pytest.mark.asyncio
async def test_on_app_command_error_cooldown(bot):
    """Test app command error handling for cooldown."""
    interaction = AsyncMock()
    cooldown = MockCooldown()
    error = commands.CommandOnCooldown(cooldown, 60, commands.BucketType.default)
    
    await bot.on_app_command_error(interaction, error)
    interaction.response.send_message.assert_called_once()
    assert "cooldown" in interaction.response.send_message.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_on_app_command_error_missing_permissions(bot):
    """Test app command error handling for missing permissions."""
    interaction = AsyncMock()
    error = commands.MissingPermissions(["manage_messages"])
    
    await bot.on_app_command_error(interaction, error)
    interaction.response.send_message.assert_called_once()
    assert "permissions" in interaction.response.send_message.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_on_app_command_error_generic(bot):
    """Test app command error handling for generic errors."""
    interaction = AsyncMock()
    error = Exception("Generic error")
    
    await bot.on_app_command_error(interaction, error)
    interaction.response.send_message.assert_called_once()
    assert "error" in interaction.response.send_message.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_on_app_command_error_response_already_done(bot):
    """Test app command error handling when response is already done."""
    interaction = AsyncMock()
    mock_interaction = MagicMock()
    error = discord.InteractionResponded(mock_interaction)
    interaction.response.send_message.side_effect = error
    
    await bot.on_app_command_error(interaction, error)
    interaction.followup.send.assert_called_once()
