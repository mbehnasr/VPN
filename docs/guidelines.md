# Project Guidelines & Q&A Log

This document consolidates operational guidelines, architectural decisions, and recurring questions captured during development.

## Repository Structure
- `services/vpn-bot/`: FastAPI + Telegram bot service (polling, APIs, Docker assets, env examples).
- `infra/`: Infrastructure-as-code (Terraform module, cloud-init bootstrap scripts).
- `deploy/`: Systemd units and alternative deployment assets.
- `design/`: Architecture documents (e.g., multi-region VPN design blueprint).
- `docs/`: Supplemental documentation, guidelines, and runbooks (this file).

## Development Workflow
1. **Local virtualenv**: Work inside `services/vpn-bot`, create `.venv`, install `requirements.txt`, run `python -m app.main`.
2. **Docker**: Use `docker compose up --build` from `services/vpn-bot` to run FastAPI and Telegram bot in a single container. Ensure `.env` is populated first.
3. **GitOps/IaC**: Terraform stack under `infra/terraform` provisions EC2, security groups, and runs `infra/scripts/cloud-init.sh` to bootstrap Docker deployment.
4. **Documentation-first**: New decisions, guidelines, or Q&A should be appended to `docs/guidelines.md` (this file) and, when architectural, to the relevant design documents under `design/`.

## Security & Secrets Handling
- **Telegram tokens & API keys**: Never commit secrets. Store in AWS SSM Parameter Store or Secrets Manager; inject via `cloud-init` or environment management.
- Rotate compromised credentials immediately (Telegram BotFather `/revoke`).
- Limit SSH ingress via Terraform variable `allowed_ssh_cidr`.

## Deployment Guidance
- **Instance Sizing (AWS EC2)**:
  - `t3.small` (2 vCPU burst, 2 GiB RAM): recommended starting point for control plane + bot.
  - `t3.medium` (2 vCPU burst, 4 GiB RAM): choose if running additional services or expecting higher concurrency.
  - `t3.large` or `m7g.medium`: future scale once database is externalized and background jobs increase.
- **Networking**: open ports 22 (restricted), 80/443 (API/Webhook), optionally V2Ray service ports.
- **Bootstrap**: `infra/scripts/cloud-init.sh` installs Docker, clones repo, runs `docker compose up -d` inside `services/vpn-bot`.

## Control Plane / Node Guidance
- Control plane uses FastAPI for REST APIs, scheduler, and admin dashboards.
- Node agents authenticate with JWT, send metrics, and pull configuration updates from `/api/v1/nodes/*` endpoints (see `design/multi-region-vpn/README.md`).
- Scheduler handles auto-accept of payments after 3 days and reassigns dynamic users when node metrics exceed thresholds.

## Telegram Bot Flow (Current MVP)
1. `/start` → language selection (English/Persian).
2. Guided plan selection: location → duration → users → data cap.
3. Price preview, payment proof upload.
4. Temporary plan (10% quota) generated pending manual review.
5. `/trial` command grants 200 MB/1-day trial once per user.
6. Admin commands `/stats`, `/approve`, `/reject`, `/nodes` planned for next iterations.

## Testing & Quality Gates
- Add unit tests for utilities (`app/vpn_utils.py`), payment flow, and bot conversation logic.
- Run `read_lints` or linter of choice after major edits.
- Keep TODOs in `TODO.md` synchronized with this guideline file.

## Future Work (from design roadmap)
- Build multi-region control plane with node agents (see `design/multi-region-vpn/README.md`).
- Implement payment gateway integrations (Stripe, Zarinpal) with webhooks.
- Develop admin dashboard (React/Next.js) over control plane APIs.
- Integrate Prometheus metrics and alerting for node health.

## Q&A Snapshots
- **Q:** Should the app and bot be containerized? **A:** Yes; Docker + Compose recommended for reproducible deployments and GitOps workflows.
- **Q:** Recommended EC2 size? **A:** Start with `t3.small`; upgrade to `t3.medium` or beyond as load grows.
- **Q:** How to manage GitOps separation? **A:** Application code resides under `services/`; infrastructure artifacts under `infra/` and `deploy/`.
- **Q:** Where is the architecture plan stored? **A:** `design/multi-region-vpn/README.md`.

## Maintenance
- Update this file whenever a new operational guideline or answer is established.
- Cross-link related documentation (e.g., design docs, Terraform README, service README).
- Consider adopting MkDocs or Docusaurus for a browsable documentation site once docs grow.
