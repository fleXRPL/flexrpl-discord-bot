import logging
from discord.ext import commands
import discord

logger = logging.getLogger(__name__)

def setup_events(bot: commands.Bot):
    """Setup bot events."""
    
    @bot.event
    async def on_ready():
        logger.info(f"Logged in as {bot.user.name}")
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for commands"
            )
        )

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        logger.error(f"Command error: {error}")
        await ctx.send(f"An error occurred: {str(error)}") 