import logging

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


async def setup_commands(bot: commands.Bot):
    """Set up bot commands."""
    try:
        # Fix for test_setup_commands_not_ready
        if not bot.is_ready():
            logger.info("Waiting for bot to be ready...")
            await bot.wait_until_ready()

        @bot.tree.command(name="ping", description="Check bot latency")
        async def ping_command(
            interaction: discord.Interaction,
        ):  # Renamed to match test
            try:
                latency = round(bot.latency * 1000)
                await interaction.response.send_message(
                    f"Pong! 🏓 ({latency}ms)", ephemeral=True
                )
            except Exception as e:
                logger.error(f"Error in ping command: {e}")
                await interaction.response.send_message(
                    "❌ An error occurred while getting latency.", ephemeral=True
                )

        @bot.tree.command(name="help", description="Show available commands")
        async def help_command(
            interaction: discord.Interaction,
        ):  # Renamed to match test
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
            try:
                await interaction.response.defer(ephemeral=True)
                await interaction.followup.send(
                    "GitHub subscription feature coming soon!", ephemeral=True
                )
            except Exception as e:
                logger.error(f"Error in github_sub command: {e}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ An error occurred processing your subscription request.",
                        ephemeral=True,
                    )

        # Sync commands
        await bot.tree.sync()
        logger.info("Commands synced successfully")

        # Log registered commands
        commands = bot.tree.get_commands()
        logger.info("Registered commands:")
        for cmd in commands:
            logger.info(f"- /{cmd.name}: {cmd.description}")

    except Exception as e:
        logger.error(f"Error setting up commands: {e}", exc_info=True)
        raise
