import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import discord
from discord import app_commands
from discord.ext import commands
from src.bot.commands import setup_commands

@pytest.fixture
async def bot():
    """Create a bot fixture for testing."""
    bot = MagicMock(spec=commands.Bot)
    bot.tree = MagicMock()
    bot.tree.sync = AsyncMock()
    bot.wait_until_ready = AsyncMock()
    bot.latency = 0.1  # 100ms latency for testing
    return bot

@pytest.mark.asyncio
async def test_setup_commands_success(bot):
    """Test successful command setup."""
    await setup_commands(bot)
    bot.tree.sync.assert_called_once()

@pytest.mark.asyncio
async def test_setup_commands_not_ready(bot):
    """Test command setup when bot is not ready."""
    bot._ready = None
    await setup_commands(bot)
    bot.wait_until_ready.assert_called_once()
    bot.tree.sync.assert_called_once()

@pytest.mark.asyncio
async def test_github_sub_command(bot):
    """Test GitHub subscription command."""
    # Store all command callbacks
    commands = {}
    def command_decorator(*args, **kwargs):
        def inner(func):
            commands[func.__name__] = func
            return func
        return inner
    bot.tree.command = command_decorator
    
    await setup_commands(bot)
    
    # Get the github_sub command
    github_sub = commands['github_sub']
    assert github_sub is not None
    
    interaction = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    
    await github_sub(interaction, repository="owner/repo")
    
    interaction.response.defer.assert_called_once_with(ephemeral=True)
    interaction.followup.send.assert_called_once_with(
        "Attempting to subscribe to repository: owner/repo",
        ephemeral=True
    )

@pytest.mark.asyncio
async def test_ping_command(bot):
    """Test ping command."""
    commands = {}
    def command_decorator(*args, **kwargs):
        def inner(func):
            commands[func.__name__] = func
            return func
        return inner
    bot.tree.command = command_decorator
    
    await setup_commands(bot)
    
    # Get the ping command
    ping = commands['ping']
    assert ping is not None
    
    interaction = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    
    await ping(interaction)
    
    interaction.response.defer.assert_called_once_with(ephemeral=True)
    interaction.followup.send.assert_called_once_with(
        "Pong! (100.00ms)",
        ephemeral=True
    )

@pytest.mark.asyncio
async def test_help_command(bot):
    """Test help command."""
    commands = {}
    def command_decorator(*args, **kwargs):
        def inner(func):
            commands[func.__name__] = func
            return func
        return inner
    bot.tree.command = command_decorator
    
    # Mock bot.tree.get_commands()
    mock_command = MagicMock()
    mock_command.name = "test"
    mock_command.description = "Test command"
    bot.tree.get_commands.return_value = [mock_command]
    
    await setup_commands(bot)
    
    # Get the help command
    help_command = commands['help_command']
    assert help_command is not None
    
    interaction = AsyncMock()
    interaction.response.send_message = AsyncMock()
    
    await help_command(interaction)
    
    interaction.response.send_message.assert_called_once_with(
        "**Available Commands:**\n`/test` - Test command",
        ephemeral=True
    )

@pytest.mark.asyncio
async def test_command_error_handling(bot):
    """Test error handling in commands."""
    commands = {}
    def command_decorator(*args, **kwargs):
        def inner(func):
            commands[func.__name__] = func
            return func
        return inner
    bot.tree.command = command_decorator
    
    await setup_commands(bot)
    
    # Test error handling in github_sub command
    github_sub = commands['github_sub']
    assert github_sub is not None
    
    interaction = AsyncMock()
    interaction.response.defer = AsyncMock(side_effect=Exception("Test error"))
    interaction.followup.send = AsyncMock()
    
    await github_sub(interaction, repository="owner/repo")
    
    interaction.followup.send.assert_called_once_with(
        "An error occurred while processing your request.",
        ephemeral=True
    )

@pytest.mark.asyncio
async def test_ping_command_error(bot):
    """Test error handling in ping command."""
    commands = {}
    def command_decorator(*args, **kwargs):
        def inner(func):
            commands[func.__name__] = func
            return func
        return inner
    bot.tree.command = command_decorator
    
    await setup_commands(bot)
    
    ping = commands['ping']
    assert ping is not None
    
    interaction = AsyncMock()
    interaction.response.defer = AsyncMock(side_effect=Exception("Test error"))
    interaction.followup.send = AsyncMock()
    
    await ping(interaction)
    
    interaction.followup.send.assert_called_once_with(
        "An error occurred while checking latency.",
        ephemeral=True
    )
