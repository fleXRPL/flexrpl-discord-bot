import logging

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


async def setup_commands(bot: commands.Bot):
    """Set up bot commands."""
    try:
        logger.info("Setting up commands...")

        @bot.tree.command(name="ping", description="Check bot latency")
        async def ping_command(interaction: discord.Interaction):
            try:
                latency = round(bot.latency * 1000)
                await interaction.response.send_message(
                    f"Pong! 🏓 ({latency}ms)", ephemeral=True
                )
            except Exception as e:
                logger.error(f"Error in ping command: {e}")
                await interaction.response.send_message(
                    "❌ Error checking latency.", ephemeral=True
                )

        @bot.tree.command(name="help", description="Show available commands")
        async def help_command(interaction: discord.Interaction):
            commands_list = [
                f"`/{cmd.name}` - {cmd.description}" for cmd in bot.tree.get_commands()
            ]
            await interaction.response.send_message(
                "**Available Commands:**\n" + "\n".join(commands_list), ephemeral=True
            )

        @bot.tree.command(
            name="githubsub", description="Subscribe to GitHub notifications"
        )
        async def github_sub(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(
                "GitHub subscription feature coming soon!", ephemeral=True
            )

        logger.info("Commands setup complete")
        return True

    except Exception as e:
        logger.error(f"Error setting up commands: {e}", exc_info=True)
        raise
