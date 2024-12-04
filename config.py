import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass

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
    ALLOWED_GUILD_IDS: list[int] = [
        int(id_) for id_ in os.getenv('ALLOWED_GUILD_IDS', '').split(',')
        if id_.strip().isdigit()
    ]
    ADMIN_USER_IDS: list[int] = [
        int(id_) for id_ in os.getenv('ADMIN_USER_IDS', '').split(',')
        if id_.strip().isdigit()
    ]

    def validate(self) -> None:
        """Validate all configuration variables."""
        missing_vars = []
        invalid_vars = []

        # Required variables and their validation rules
        required_configs = {
            'DISCORD_BOT_TOKEN': lambda x: len(x) > 50,  # Discord tokens are typically long
            'DISCORD_PUBLIC_KEY': lambda x: len(x) == 32,  # Public keys are 32 chars
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