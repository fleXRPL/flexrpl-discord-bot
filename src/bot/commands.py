from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

async def setup_commands(bot: commands.Bot):
    """Setup bot commands."""
    
    @bot.tree.command(name="ping", description="Check bot latency")
    async def ping(interaction):
        await interaction.response.send_message(f"Pong! ({bot.latency*1000:.2f}ms)")

    @bot.tree.command(name="help", description="Show available commands")
    async def help_command(interaction):
        commands_list = [
            command.name for command in bot.tree.get_commands()
        ]
        await interaction.response.send_message(
            f"Available commands: {', '.join(commands_list)}"
        )

    await bot.tree.sync() 