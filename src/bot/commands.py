from discord.ext import commands
from discord import app_commands
import discord
import logging

logger = logging.getLogger(__name__)


async def setup_commands(bot: commands.Bot):
    """Setup bot commands."""
    try:
        @bot.tree.command(
            name="githubsub",
            description="Subscribe to GitHub notifications"
        )
        @app_commands.describe(
            repository="The GitHub repository to subscribe to (format: owner/repo)"
        )
        async def github_sub(interaction: discord.Interaction, repository: str):
            try:
                await interaction.response.defer(ephemeral=True)
                await interaction.followup.send(
                    f"Attempting to subscribe to repository: {repository}",
                    ephemeral=True
                )
            except Exception as e:
                logger.error(f"Error in githubsub command: {e}")
                await interaction.followup.send(
                    "An error occurred while processing your request.",
                    ephemeral=True
                )

        @bot.tree.command(name="ping", description="Check bot latency")
        async def ping(interaction: discord.Interaction):
            try:
                await interaction.response.send_message(
                    f"Pong! ({bot.latency*1000:.2f}ms)",
                    ephemeral=True
                )
            except Exception as e:
                logger.error(f"Error in ping command: {e}")
                await interaction.followup.send(
                    "An error occurred while checking latency.",
                    ephemeral=True
                )

        @bot.tree.command(name="help", description="Show available commands")
        async def help_command(interaction: discord.Interaction):
            try:
                commands_list = [
                    f"`/{command.name}` - {command.description}"
                    for command in bot.tree.get_commands()
                ]
                await interaction.response.send_message(
                    "**Available Commands:**\n" + "\n".join(commands_list),
                    ephemeral=True
                )
            except Exception as e:
                logger.error(f"Error in help command: {e}")
                await interaction.followup.send(
                    "An error occurred while fetching commands.",
                    ephemeral=True
                )

        if not hasattr(bot, '_ready') or bot._ready is None:
            logger.warning("Bot not ready, waiting before syncing commands...")
            await bot.wait_until_ready()

        await bot.tree.sync()
        logger.info("Commands synced successfully")

    except Exception as e:
        logger.error(f"Error setting up commands: {e}")
        raise
