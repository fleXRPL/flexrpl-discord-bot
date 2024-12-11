import pytest
from unittest.mock import AsyncMock, MagicMock
from discord.ext import commands
from src.bot.commands import setup_commands

@pytest.fixture
async def bot():
    """Create a bot fixture for testing."""
    bot = MagicMock(spec=commands.Bot)
    bot.tree = MagicMock()
    bot.tree.command = MagicMock()
    bot.tree.sync = AsyncMock()
    bot.latency = 0.1  # 100ms latency for testing
    return bot

@pytest.mark.asyncio
async def test_setup_commands_success(bot):
    """Test successful command setup."""
    result = await setup_commands(bot)
    assert result is True
    # Verify commands were registered
    assert bot.tree.command.called

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
    
    ping_command = commands['ping_command']
    assert ping_command is not None

    interaction = AsyncMock()
    await ping_command(interaction)
    
    interaction.response.send_message.assert_called_once_with(
        "Pong! 🏓 (100ms)",
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

    # Create proper mock commands with name attributes
    cmd1 = MagicMock()
    cmd1.name = "test1"
    cmd1.description = "Test command 1"
    
    cmd2 = MagicMock()
    cmd2.name = "test2"
    cmd2.description = "Test command 2"
    
    # Mock get_commands to return our properly configured mock commands
    bot.tree.get_commands = MagicMock(return_value=[cmd1, cmd2])

    await setup_commands(bot)
    
    help_command = commands['help_command']
    assert help_command is not None

    interaction = AsyncMock()
    await help_command(interaction)
    
    # Verify help message was sent with correct arguments
    interaction.response.send_message.assert_called_once_with(
        "**Available Commands:**\n`/test1` - Test command 1\n`/test2` - Test command 2",
        ephemeral=True
    )

@pytest.mark.asyncio
async def test_github_sub_command(bot):
    """Test GitHub subscription command."""
    commands = {}
    def command_decorator(*args, **kwargs):
        def inner(func):
            commands[func.__name__] = func
            return func
        return inner
    bot.tree.command = command_decorator

    await setup_commands(bot)
    
    githubsub = commands['githubsub_command']
    assert githubsub is not None

    interaction = AsyncMock()
    await githubsub(interaction)
    
    # Verify defer was called with ephemeral=True
    interaction.response.defer.assert_called_once_with(ephemeral=True)

@pytest.mark.asyncio
async def test_setup_commands_error(bot):
    """Test error handling in command setup."""
    bot.tree.command.side_effect = Exception("Test error")
    
    with pytest.raises(Exception):
        await setup_commands(bot)
