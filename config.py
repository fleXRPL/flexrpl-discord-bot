import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    """Application configuration."""
    DISCORD_TOKEN: str = os.getenv('DISCORD_TOKEN', '')
    DISCORD_GUILD_ID: Optional[int] = int(os.getenv('DISCORD_GUILD_ID', 0))
    GITHUB_WEBHOOK_SECRET: str = os.getenv('GITHUB_WEBHOOK_SECRET', '')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    DATABASE_URL: str = os.getenv('DATABASE_URL', '')

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration variables."""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN must be set")
        if not cls.DISCORD_GUILD_ID:
            raise ValueError("DISCORD_GUILD_ID must be set")
        if not cls.GITHUB_WEBHOOK_SECRET:
            raise ValueError("GITHUB_WEBHOOK_SECRET must be set")

config = Config() 