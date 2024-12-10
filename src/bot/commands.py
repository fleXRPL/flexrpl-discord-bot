import logging

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


async def setup_commands(bot: commands.Bot):
    """Setup bot commands."""
    try:

        @bot.tree.command(
            name="githubsub", description="Subscribe to GitHub notifications"
        )
        @app_commands.describe(
            repository="The GitHub repository to subscribe to (format: owner/repo)"
        )
        async def github_sub(interaction: discord.Interaction, repository: str):
            """Handle GitHub subscription command."""
            try:
                logger.info(
                    f"Processing githubsub command for repository: {repository}"
                )
                await interaction.response.defer(ephemeral=True)
                logger.debug("Response deferred")

                # Add processing logic here
                await interaction.followup.send(
                    f"✅ Attempting to subscribe to repository: {repository}",
                    ephemeral=True,
                )
                logger.info(f"Subscription request processed for: {repository}")
            except Exception as e:
                logger.error(f"Error in githubsub command: {e}", exc_info=True)
                message = (
                    "❌ An error occurred while processing your subscription request."
                )
                if not interaction.response.is_done():
                    await interaction.response.send_message(message, ephemeral=True)
                else:
                    await interaction.followup.send(message, ephemeral=True)

        @bot.tree.command(name="ping", description="Check bot latency")
        async def ping(interaction: discord.Interaction):
            """Handle ping command."""
            try:
                logger.info("Processing ping command")
                latency = round(bot.latency * 1000)
                await interaction.response.send_message(
                    f"Pong! 🏓 ({latency}ms)", ephemeral=True
                )
                logger.info(f"Ping command completed. Latency: {latency}ms")
            except Exception as e:
                logger.error(f"Error in ping command: {e}", exc_info=True)
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ An error occurred while checking latency.", ephemeral=True
                    )

        @bot.tree.command(name="help", description="Show available commands")
        async def help_command(interaction: discord.Interaction):
            """Handle help command."""
            try:
                logger.info("Processing help command")
                commands_list = [
                    f"`/{command.name}` - {command.description}"
                    for command in bot.tree.get_commands()
                ]
                logger.debug(f"Available commands: {commands_list}")

                await interaction.response.send_message(
                    "**Available Commands:**\n" + "\n".join(commands_list),
                    ephemeral=True,
                )
                logger.info("Help command completed successfully")
            except Exception as e:
                logger.error(f"Error in help command: {e}", exc_info=True)
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ An error occurred while fetching commands.", ephemeral=True
                    )

        if not hasattr(bot, "_ready") or bot._ready is None:
            logger.warning("Bot not ready, waiting before syncing commands...")
            await bot.wait_until_ready()

        await bot.tree.sync()
        logger.info("Commands synced successfully")

    except Exception as e:
        logger.error(f"Error setting up commands: {e}")
        raise
