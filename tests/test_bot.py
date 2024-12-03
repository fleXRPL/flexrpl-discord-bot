import pytest
from discord.ext import commands
from src.bot.commands import setup_commands
from src.bot.events import setup_events

@pytest.fixture
def bot():
    return commands.Bot(command_prefix="!")

@pytest.mark.asyncio
async def test_setup_commands(bot):
    await setup_commands(bot)
    assert any(cmd.name == "ping" for cmd in bot.tree.get_commands())
    assert any(cmd.name == "help" for cmd in bot.tree.get_commands())

def test_setup_events(bot):
    setup_events(bot)
    assert bot.extra_events.get('on_ready')
    assert bot.extra_events.get('on_command_error') 