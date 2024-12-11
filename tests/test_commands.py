import pytest
from unittest.mock import AsyncMock, MagicMock
from discord.ext import commands

@pytest.fixture
async def bot():
    """Create a bot fixture for testing."""
    bot = MagicMock(spec=commands.Bot)
    bot.tree = MagicMock()
    bot.tree.command = MagicMock()
    bot.tree.sync = AsyncMock()
    bot.latency = 0.1
    return bot

@pytest.mark.asyncio
async def test_githubsub_command(bot):
    """Test GitHub subscription command."""
    from src.bot.commands import setup_commands
    
    # Setup mock command tree
    commands = {}
    def command_decorator(*args, **kwargs):
        def inner(func):
            name = kwargs.get('name', func.__name__)
            commands[name] = func
            return func
        return inner
    bot.tree.command = command_decorator

    # Setup commands
    await setup_commands(bot)

    # Get the githubsub command
    githubsub = commands.get('githubsub')
    assert githubsub is not None

    # Test the command
    interaction = AsyncMock()
    await githubsub(interaction)

    # Verify defer was called with ephemeral=True
    interaction.response.defer.assert_called_once_with(ephemeral=True)
