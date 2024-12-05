import pytest
from discord.ext import commands
import os
from unittest.mock import patch
from src.bot.bot import FlexRPLBot

@pytest.mark.asyncio
@patch.dict(os.environ, {'DISCORD_APPLICATION_ID': '123456789'})
async def test_bot_initialization():
    bot = FlexRPLBot()
    assert isinstance(bot, commands.Bot)
    assert bot.command_prefix == "!"
    assert bot.application_id == '123456789' 