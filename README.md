# fleXRPL Discord Bot

A Discord bot for GitHub notifications and repository management for the fleXRPL organization.

## Features

- GitHub webhook integration
- Repository event notifications
- Command-based subscription management
- Role-based access control

## Prerequisites

- Python 3.9+
- Discord Developer Account
- GitHub Organization Admin access
- Railway.app Account

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
python app.py
```

## Deployment on Railway.app

1. Fork this repository
2. Create new project on Railway.app
3. Connect your GitHub repository
4. Add environment variables in Railway dashboard
5. Deploy!

## Environment Variables

- `DISCORD_PUBLIC_KEY`: Your Discord application public key
- `DISCORD_BOT_TOKEN`: Your Discord bot token
- `GITHUB_WEBHOOK_SECRET`: Secret for GitHub webhooks
- `ALLOWED_CHANNELS`: Comma-separated list of allowed Discord channel IDs

## Contributing

Please read our [Contributing Guidelines](https://github.com/fleXRPL/fleXRP/blob/main/CONTRIBUTING.md) before submitting changes.

## License

This project is licensed under the MIT License - see the (https://github.com/fleXRPL/fleXRP/blob/main/LICENSE) file for details.