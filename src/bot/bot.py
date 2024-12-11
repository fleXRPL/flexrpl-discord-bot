import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from .commands import setup_commands
from .events import setup_events

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FlexRPLBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            application_id=os.getenv("DISCORD_APPLICATION_ID"),
        )

        # Set up error handler
        self.tree.error(self.on_app_command_error)

    async def setup_hook(self):
        """Initialize the bot with required setup."""
        try:
            logger.info("Setting up bot...")
            await setup_events(self)
            # Setup commands
            await setup_commands(self)

            # Sync commands globally
            await self.tree.sync()
            logger.info("Bot commands synced successfully")

            # Log available commands
            commands = self.tree.get_commands()
            logger.info("Available commands after sync:")
            for cmd in commands:
                logger.info(f"- /{cmd.name}: {cmd.description}")

        except Exception as e:
            logger.error(f"Error in setup_hook: {e}", exc_info=True)
            raise

    async def on_ready(self):
        """Event handler for when the bot is ready."""
        logger.info(f"Logged in as {self.user.name} (ID: {self.user.id})")
        logger.info("------")
        logger.info("Registered commands:")
        for cmd in self.tree.get_commands():
            logger.info(f"- /{cmd.name}: {cmd.description}")

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        """Handle errors from application commands."""
        try:
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True)

            if isinstance(error, app_commands.CommandOnCooldown):
                await interaction.followup.send(
                    f"This command is on cooldown. "
                    f"Try again in {error.retry_after:.2f}s",
                    ephemeral=True,
                )
            elif isinstance(error, app_commands.MissingPermissions):
                await interaction.followup.send(
                    "You don't have permission to use this command.", ephemeral=True
                )
            else:
                logger.error(f"Command error: {error}", exc_info=error)
                await interaction.followup.send(
                    "An error occurred while processing the command.", ephemeral=True
                )
        except Exception as e:
            logger.error(f"Error in error handler: {e}")


bot = FlexRPLBot()
