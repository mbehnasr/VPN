# VPN Sales Bot Service

FastAPI + Telegram bot that manages V2Ray VPN trials and paid plans.

## Local Development (venv)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

## Docker

```bash
docker compose up --build
```

The container listens on `8000` and runs both the FastAPI API and the Telegram bot via polling.

## Environment

Populate `.env` with the required settings (see `.env.example`). For production use, prefer injecting secrets from AWS SSM Parameter Store or Secrets Manager.

## Tests (future)

Add pytest-based unit tests for conversation flows, database helpers, and utility functions as the project evolves.

