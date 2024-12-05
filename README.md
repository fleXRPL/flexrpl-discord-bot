# fleXRPL Discord Bot

[![Railway Deploy](https://img.shields.io/badge/Railway-Deployed-success)](https://railway.app)
[![GitHub Actions](https://github.com/fleXRPL/flexrpl-discord-bot/actions/workflows/deploy.yml/badge.svg)](https://github.com/fleXRPL/flexrpl-discord-bot/actions)

A Discord bot for GitHub notifications and repository management for the fleXRPL organization.

## Features

- GitHub webhook integration
- Repository event notifications
- Command-based subscription management
- Role-based access control

## Prerequisites

- Python 3.11+ (updated to match Railway.app environment)
- Discord Developer Account
- GitHub Organization Admin access
- Railway.app Account

## Repo Structure

```bash
.flexrpl-discord-bot/
├── Dockerfile
├── Procfile
├── README.md
├── app.py
├── config.py
├── requirements-dev.txt
├── requirements.txt
├── runtime.txt
├── setup.cfg
├── src
│   ├── bot
│   │   ├── __init__.py
│   │   ├── commands.py
│   │   └── events.py
│   ├── handlers
│   │   └── github_webhook.py
│   └── utils
│       └── formatting.py
└── tests
    ├── test_bot.py
    └── test_formatting.py

6 directories, 16 files
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

4. Run linting manually:
```bash
flake8 src tests
black src tests
isort src tests
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
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Deployment on Railway.app

1. Fork this repository
2. Create new project on Railway.app
3. Connect your GitHub repository
4. Add required environment variables in Railway dashboard:
   - `DISCORD_PUBLIC_KEY`
   - `DISCORD_APPLICATION_ID`
   - `DISCORD_BOT_TOKEN`
   - `DISCORD_CLIENT_ID`
   - `GITHUB_WEBHOOK_SECRET`
   - `PORT` (default: 8000)
5. Deploy!

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

## Contributing

Please read our [Contributing Guidelines](https://github.com/fleXRPL/fleXRP/blob/main/CONTRIBUTING.md) before submitting changes.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/fleXRPL/fleXRP/blob/main/LICENSE) file for details.
