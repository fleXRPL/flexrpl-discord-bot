import logging

import discord

logger = logging.getLogger(__name__)


async def setup_commands(bot_instance):
    """Set up bot commands."""
    try:
        logger.info("Setting up commands...")

        @bot_instance.tree.command(name="ping", description="Check bot latency")
        async def ping_command(interaction: discord.Interaction):
            """Check bot latency."""
            try:
                latency = round(bot_instance.latency * 1000)
                await interaction.response.send_message(
                    f"Pong! 🏓 (Latency: {latency}ms)", ephemeral=True
                )
            except Exception as e:
                logger.error(f"Error in ping command: {e}")
                await interaction.response.send_message(
                    "Pong! 🏓 (Latency unavailable)", ephemeral=True
                )

        @bot_instance.tree.command(name="help", description="Show available commands")
        async def help_command(interaction: discord.Interaction):
            """Show available commands."""
            try:
                commands = bot_instance.tree.get_commands()
                commands_list = [
                    f"`/{cmd.name}` - {cmd.description}" for cmd in commands
                ]
                await interaction.response.send_message(
                    "**Available Commands:**\n" + "\n".join(commands_list),
                    ephemeral=True,
                )
            except Exception as e:
                logger.error(f"Error in help command: {e}")
                await interaction.response.send_message(
                    "❌ Error retrieving commands.", ephemeral=True
                )

        @bot_instance.tree.command(
            name="githubsub", description="Subscribe to GitHub notifications"
        )
        async def githubsub_command(interaction: discord.Interaction):
            """Subscribe to GitHub notifications."""
            try:
                await interaction.response.defer(ephemeral=True)
                # Deferred response will be handled by webhook
            except Exception as e:
                logger.error(f"Error in githubsub command: {e}")
                await interaction.response.send_message(
                    "❌ Error processing subscription.", ephemeral=True
                )

        logger.info("Commands setup complete")
        return True

    except Exception as e:
        logger.error(f"Error setting up commands: {e}")
        raise
