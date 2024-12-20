# fleXRPL Discord Bot

[![Railway Deploy](https://img.shields.io/badge/Railway-Deployed-success)](https://railway.app)
[![GitHub Actions](https://github.com/fleXRPL/flexrpl-discord-bot/actions/workflows/deploy.yml/badge.svg)](https://github.com/fleXRPL/flexrpl-discord-bot/actions)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=fleXRPL_flexrpl-discord-bot&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=fleXRPL_flexrpl-discord-bot)

A Discord bot for GitHub notifications and repository management for the fleXRPL organization.

## Features

- GitHub webhook integration
- Repository event notifications
- Command-based subscription management
- Role-based access control
- Comprehensive logging system
- Secure command handling with deferred responses

## Available Commands

- `/githubsub` - Subscribe to GitHub notifications
- `/help` - Show available commands
- `/ping` - Check bot latency

## Prerequisites

- Python 3.11+ (updated to match Railway.app environment)
- Discord Developer Account
- GitHub Organization Admin access
- Railway.app Account

## Repo Structure

```bash
.flexrpl-discord-bot/
├── Dockerfile
├── PRIVACY_POLICY.md
├── Procfile
├── README.md
├── TERMS_OF_SERVICE.md
├── app.py
├── config.py
├── format_and_lint.sh
├── requirements-dev.txt
├── requirements.txt
├── runtime.txt
├── setup.cfg
├── src
│   ├── bot
│   │   ├── __init__.py
│   │   ├── bot.py
│   │   ├── commands.py
│   │   └── events.py
│   ├── handlers
│   │   └── github_webhook.py
│   ├── main.py
│   ├── routes
│   │   └── discord.py
│   └── utils
│       └── formatting.py
└── tests
    ├── conftest.py
    ├── test_bot.py
    ├── test_commands.py
    ├── test_discord_routes.py
    ├── test_events.py
    ├── test_formatting.py
    └── test_main.py

13 directories, 48 files
```
## Development Setup

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

3. Run tests:
```bash
pytest
```

4. Run linting and formatting:
```bash
bash format_and_lint.sh
```

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/fleXRPL/flexrpl-discord-bot.git
cd flexrpl-discord-bot
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Unix
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # for development
```

4. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Variables

Required variables:
- `DISCORD_PUBLIC_KEY`: Your Discord application public key
- `DISCORD_APPLICATION_ID`: Your Discord application ID
- `DISCORD_BOT_TOKEN`: Your Discord bot token
- `DISCORD_CLIENT_ID`: Your Discord client ID
- `GITHUB_WEBHOOK_SECRET`: Secret for GitHub webhooks
- `PORT`: Port for the application to run on (default: 8000)

Optional variables:
- `LOG_LEVEL`: Logging level (default: INFO)
- `ALLOWED_GUILD_IDS`: Comma-separated list of allowed Discord server IDs
- `ADMIN_USER_IDS`: Comma-separated list of Discord admin user IDs

## Deployment on Railway.app

1. Fork this repository
2. Create new project on Railway.app
3. Connect your GitHub repository
4. Add required environment variables in Railway dashboard
5. Deploy!

## Testing

The bot includes comprehensive tests:
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_discord_routes.py -v
```

## Logging

The bot includes detailed logging for troubleshooting:
- Request/response logging for all interactions
- Command processing logs
- Error tracking with stack traces
- Performance metrics

## Contributing

Please read our [Contributing Guidelines](https://github.com/fleXRPL/fleXRP/blob/main/CONTRIBUTING.md) before submitting changes.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/fleXRPL/fleXRP/blob/main/LICENSE) file for details.
