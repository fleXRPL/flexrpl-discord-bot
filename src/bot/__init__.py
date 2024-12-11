from .bot import FlexRPLBot, bot
from .commands import setup_commands
from .events import setup_events

__all__ = ["bot", "FlexRPLBot", "setup_commands", "setup_events"]

VERSION = "1.0.0"
