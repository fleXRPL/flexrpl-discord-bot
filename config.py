import os
from dataclasses import dataclass, field
from typing import Optional, List
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass

def parse_guild_ids() -> List[int]:
    """Parse guild IDs from environment variable."""
    guild_ids = os.getenv('ALLOWED_GUILD_IDS', '')
    return [int(id_) for id_ in guild_ids.split(',') if id_.strip().isdigit()]

def parse_admin_ids() -> List[int]:
    """Parse admin IDs from environment variable."""
    admin_ids = os.getenv('ADMIN_USER_IDS', '')
    return [int(id_) for id_ in admin_ids.split(',') if id_.strip().isdigit()]

@dataclass
class Config:
    """Application configuration."""
    DISCORD_BOT_TOKEN: str = os.getenv('DISCORD_BOT_TOKEN', '')
    DISCORD_PUBLIC_KEY: str = os.getenv('DISCORD_PUBLIC_KEY', '')
    DISCORD_APPLICATION_ID: str = os.getenv('DISCORD_APPLICATION_ID', '')
    DISCORD_CLIENT_ID: str = os.getenv('DISCORD_CLIENT_ID', '')
    GITHUB_WEBHOOK_SECRET: str = os.getenv('GITHUB_WEBHOOK_SECRET', '')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    PORT: int = int(os.getenv('PORT', '8000'))
    ALLOWED_GUILD_IDS: List[int] = field(default_factory=parse_guild_ids)
    ADMIN_USER_IDS: List[int] = field(default_factory=parse_admin_ids)

    def validate(self) -> None:
        """Validate all configuration variables."""
        missing_vars = []
        invalid_vars = []

        # Required variables and their validation rules
        required_configs = {
            'DISCORD_BOT_TOKEN': lambda x: len(x) > 50,
            'DISCORD_PUBLIC_KEY': lambda x: len(x) == 32,
            'DISCORD_APPLICATION_ID': lambda x: x.isdigit(),
            'DISCORD_CLIENT_ID': lambda x: x.isdigit(),
            'GITHUB_WEBHOOK_SECRET': lambda x: len(x) > 8
        }

        for var_name, validation_rule in required_configs.items():
            value = getattr(self, var_name)
            if not value:
                missing_vars.append(var_name)
            elif not validation_rule(value):
                invalid_vars.append(var_name)

        # Validate PORT
        try:
            port = int(self.PORT)
            if not (1024 <= port <= 65535):
                invalid_vars.append('PORT')
        except ValueError:
            invalid_vars.append('PORT')

        # Validate LOG_LEVEL
        valid_log_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if self.LOG_LEVEL.upper() not in valid_log_levels:
            invalid_vars.append('LOG_LEVEL')

        # Raise error if any validations failed
        if missing_vars or invalid_vars:
            error_msg = []
            if missing_vars:
                error_msg.append(f"Missing required variables: {', '.join(missing_vars)}")
            if invalid_vars:
                error_msg.append(f"Invalid variable values: {', '.join(invalid_vars)}")
            raise ConfigValidationError('\n'.join(error_msg))

        logger.info("Configuration validation successful")

config = Config() 