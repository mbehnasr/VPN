# VPN Sales Telegram Bot (Sample MVP)

This repository contains:

- A FastAPI application bundled with a Telegram bot (`services/vpn-bot`).
- Infrastructure-as-code definitions and GitOps assets (`infra`, `deploy`).

## Repository Layout

- `services/vpn-bot/` – Application source, Docker assets, service-level README.
- `infra/terraform/` – Terraform module that provisions AWS networking + EC2.
- `infra/scripts/` – Cloud-init bootstrap scripts invoked by Terraform.
- `deploy/systemd/` – Sample systemd units for bare-metal or VM deployments without Docker.
- `design/` – Architecture documents (e.g., multi-region VPN blueprint).
- `docs/` – Operational guidelines and Q&A (`docs/guidelines.md`).
- `TODO.md` – Roadmap and future enhancements.

## Quick Start (virtualenv)

```bash
cd services/vpn-bot
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

The bot uses polling by default. The FastAPI API runs on `http://0.0.0.0:8000`.

## Docker Workflow

Build and run locally from the service directory:

```bash
cd services/vpn-bot
docker compose up --build
```

Update `.env` before launching; the container exposes port `8000`.

## GitOps / Terraform

Sample Terraform configuration lives in `infra/terraform`. Configure your AWS credentials and remote backend, then:

```bash
cd infra/terraform
terraform init
terraform plan \
  -var="vpc_id=..." \
  -var="subnet_id=..." \
  -var="key_name=..."
terraform apply
```

The included `infra/scripts/cloud-init.sh` installs Docker on the EC2 instance, clones this repo, and launches the stack via Compose.

## Useful Endpoints

- `GET /health`
- `GET /admin/users`
- `GET /admin/payments`
- `GET /admin/usages`

## Deployment Notes

- `infra/scripts/cloud-init.sh` – Bootstrap script executed by Terraform-provisioned EC2.
- `deploy/systemd/vpn-bot.service` – Sample unit if you deploy without Docker.
