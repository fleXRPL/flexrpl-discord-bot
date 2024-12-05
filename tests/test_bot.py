import pytest
from discord.ext import commands
from src.bot.bot import FlexRPLBot

@pytest.mark.asyncio
async def test_bot_initialization():
    bot = FlexRPLBot()
    assert isinstance(bot, commands.Bot)
    assert bot.command_prefix == "!" 