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
        super().__init__(
            command_prefix="!",
            intents=intents,
            application_id=config.DISCORD_APPLICATION_ID
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