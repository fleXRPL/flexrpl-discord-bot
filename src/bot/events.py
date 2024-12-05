import logging

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


def setup_events(bot: commands.Bot):
    """Setup bot events."""

    @bot.event
    async def on_guild_join(guild: discord.Guild):
        logger.info(f"Bot has been added to guild: {guild.name} (ID: {guild.id})")

    @bot.event
    async def on_guild_remove(guild: discord.Guild):
        logger.info(f"Bot has been removed from guild: {guild.name} (ID: {guild.id})")

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        logger.error(f"Command error: {error}")
        await ctx.send(f"An error occurred: {str(error)}")
