import pytest
from discord.ext import commands
import os
from unittest.mock import patch, AsyncMock, MagicMock
from src.bot.bot import FlexRPLBot

@pytest.mark.asyncio
@patch.dict(os.environ, {'DISCORD_APPLICATION_ID': '123456789'})
async def test_bot_initialization():
    bot = FlexRPLBot()
    assert isinstance(bot, commands.Bot)
    assert bot.command_prefix == "!"
    assert bot.application_id == 123456789
    assert bot.intents.message_content is True
    assert bot.intents.guilds is True

@pytest.mark.asyncio
@patch.dict(os.environ, {'DISCORD_APPLICATION_ID': '123456789'})
async def test_bot_setup_hook():
    bot = FlexRPLBot()
    bot.tree.sync = AsyncMock()
    bot._ready = MagicMock()
    bot._ready.wait = AsyncMock()
    bot.wait_until_ready = AsyncMock()
    
    with patch('src.bot.bot.setup_commands', new_callable=AsyncMock) as mock_setup_commands:
        with patch('src.bot.bot.setup_events') as mock_setup_events:
            await bot.setup_hook()
            
            mock_setup_commands.assert_called_once_with(bot)
            mock_setup_events.assert_called_once_with(bot)
            bot.tree.sync.assert_called_once() 