import discord
from discord.ext import commands
from discord import app_commands
import logging
import os
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
            application_id=os.getenv('DISCORD_APPLICATION_ID')
        )
        
        # Set up error handler
        self.tree.error(self.on_app_command_error)
        
    async def setup_hook(self):
        """Setup hook that runs before the bot starts."""
        try:
            await setup_commands(self)
            setup_events(self)
            await self.tree.sync()
            logger.info("Bot commands synced successfully")
        except Exception as e:
            logger.error(f"Error in setup hook: {e}")
            raise

    async def on_ready(self):
        """Event handler for when the bot is ready."""
        logger.info(f"Logged in as {self.user.name} (ID: {self.user.id})")
        logger.info("------")
        logger.info("Registered commands:")
        for cmd in self.tree.get_commands():
            logger.info(f"- /{cmd.name}: {cmd.description}")

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """Handle errors from application commands."""
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Try again in {error.retry_after:.2f}s",
                ephemeral=True
            )
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You don't have permission to use this command.",
                ephemeral=True
            )
        else:
            logger.error(f"Command error: {error}", exc_info=error)
            await interaction.response.send_message(
                "An error occurred while processing the command.",
                ephemeral=True
            )