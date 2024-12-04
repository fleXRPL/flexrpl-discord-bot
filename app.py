import discord
from discord import app_commands
from discord.ext import commands
from config import config
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup bot
intents = discord.Intents.default()
intents.message_content = True

class Bot(commands.Bot):
    def __init__(self):
        # Define permissions for the bot
        permissions = discord.Permissions(
            send_messages=True,
            send_messages_in_threads=True,
            create_public_threads=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            use_slash_commands=True,
            view_channel=True,
            read_messages=True
        )
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            application_id=config.DISCORD_APPLICATION_ID,
            permissions=permissions
        )

    async def setup_hook(self):
        """Setup bot hooks."""
        await self.tree.sync()
        logger.info("Command tree synced")

bot = Bot()

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! ({bot.latency*1000:.2f}ms)")

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")

def run_bot():
    """Run the bot."""
    bot.run(config.DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    run_bot() 