from discord.ext import commands
from discord import app_commands
import discord
import logging

logger = logging.getLogger(__name__)

async def setup_commands(bot: commands.Bot):
    """Setup bot commands."""
    try:
        @bot.tree.command(name="ping", description="Check bot latency")
        async def ping(interaction: discord.Interaction):
            await interaction.response.send_message(f"Pong! ({bot.latency*1000:.2f}ms)")

        @bot.tree.command(name="help", description="Show available commands")
        async def help_command(interaction: discord.Interaction):
            commands_list = [
                command.name for command in bot.tree.get_commands()
            ]
            await interaction.response.send_message(
                f"Available commands: {', '.join(commands_list)}"
            )

        logger.info("Syncing commands...")
        await bot.tree.sync()
        logger.info("Commands synced successfully")
        
    except Exception as e:
        logger.error(f"Error setting up commands: {e}")
        raise 