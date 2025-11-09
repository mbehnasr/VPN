# VPN Sales Telegram Bot (Sample MVP)

This repository contains a FastAPI application bundled with a Telegram bot for selling V2Ray VPN plans and granting trial access.

## Quick Start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

The bot uses polling by default. The FastAPI API runs on `http://0.0.0.0:8000`.

## Useful Endpoints

- `GET /health`
- `GET /admin/users`
- `GET /admin/payments`
- `GET /admin/usages`

## Deployment Notes

See `scripts/systemd/vpn-bot.service` for a sample systemd unit that launches both the Telegram bot and FastAPI app using `uvicorn`.
