import logging

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class FlexRPLBot(commands.Bot):
    """Custom bot class for FlexRPL."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        """Set up bot hooks and sync commands."""
        try:
            logger.info("Setting up bot...")
            # Import here to avoid circular imports
            from src.bot.commands import setup_commands
            from src.bot.events import setup_events

            await setup_commands(self)
            await setup_events(self)

            # Sync commands with Discord
            await self.tree.sync()

            # Log available commands
            commands = self.tree.get_commands()
            logger.info("Available commands after sync:")
            for cmd in commands:
                logger.info(f"- /{cmd.name}: {cmd.description}")

            logger.info("Bot commands synced successfully")

        except Exception as e:
            logger.error(f"Error in setup hook: {e}")
            raise

    async def on_ready(self):
        """Handle bot ready event."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info("------")
        logger.info("Registered commands:")
        commands = self.tree.get_commands()
        for cmd in commands:
            logger.info(f"- /{cmd.name}: {cmd.description}")

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: Exception
    ):
        """Handle application command errors."""
        try:
            if isinstance(error, commands.CommandOnCooldown):
                await interaction.response.send_message(
                    f"Command is on cooldown. Try again in {error.retry_after:.1f}s",
                    ephemeral=True,
                )
            elif isinstance(error, commands.MissingPermissions):
                await interaction.response.send_message(
                    "You don't have permission to use this command", ephemeral=True
                )
            elif isinstance(error, discord.InteractionResponded):
                await interaction.followup.send(
                    "An error occurred while processing your command", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "An error occurred while processing your command", ephemeral=True
                )
        except discord.InteractionResponded:
            try:
                await interaction.followup.send(
                    "An error occurred while processing your command", ephemeral=True
                )
            except Exception as e:
                logger.error(f"Error sending error message: {e}")


# Create bot instance
bot = FlexRPLBot()
