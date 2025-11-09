# Multi-Region VPN System Design

This document outlines a production-ready architecture for a multi-region VPN platform that sells V2Ray/VLESS connectivity. The FastAPI control plane manages sales, users, nodes, payments, and telemetry, while a Telegram bot serves as the user-facing interface.

---

## 1. High-Level Architecture

```mermaid
graph LR
    subgraph Users
        TG[Telegram Client]
    end

    subgraph ControlPlane[Control Plane (FastAPI)]
        API[REST / WebSocket APIs]
        DB[(PostgreSQL / SQLite)]
        Scheduler[Jobs & Auto-Heal]
        Admin[Admin Dashboard]
    end

    subgraph DataPlane[VPN Nodes]
        NodeA[V2Ray/XRay Node A]
        NodeB[V2Ray/XRay Node B]
        NodeC[V2Ray/XRay Node C]
    end

    subgraph Automation
        GitOps[GitOps / CI/CD]
        Registry[Container Registry]
    end

    TG -- HTTPS --> API
    API -- gRPC/Webhook --> TG
    NodeA -- JWT API --> API
    NodeB -- JWT API --> API
    NodeC -- JWT API --> API
    Scheduler -- health checks --> DataPlane
    Admin -- HTTPS --> API
    GitOps -- deploy configs --> DataPlane
```

### Component Summary
- **Control Plane (FastAPI)**: central brain for authentication, plan logic, billing, node orchestration, and health monitoring. Exposes REST APIs for nodes and the bot, plus admin dashboards.
- **Data Plane (V2Ray/VLESS Nodes)**: lightweight agents running alongside V2Ray/XRay servers, responsible for registering with the control plane, syncing configurations, and streaming metrics.
- **Telegram Bot**: customer interface for buying plans, requesting trials, viewing active configurations, and communicating with admins.
- **GitOps Pipeline**: Terraform/Ansible (or Kubernetes manifests) for provisioning new nodes, updating configurations, and rolling upgrades.

---

## 2. Database Schema (Core Tables)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `users` | Telegram users and admins | `id`, `telegram_id`, `username`, `language`, `is_admin`, `ban_reason`, `created_at`
| `plans` | Catalog of VPN offers | `id`, `name`, `location_tag`, `duration_days`, `max_devices`, `data_limit_mb`, `is_constant_ip`, `price_cents`
| `payments` | Payment attempts and status | `id`, `user_id`, `plan_id`, `amount_cents`, `status`, `evidence_file_id`, `auto_accept_at`, `reviewed_by`
| `nodes` | VPN nodes metadata | `id`, `name`, `public_ip`, `region`, `location_tag`, `status`, `capacity_score`, `jwt_secret`, `last_seen_at`
| `node_metrics` | Time-series metrics from nodes | `id`, `node_id`, `cpu`, `mem`, `bandwidth_in`, `bandwidth_out`, `latency_ms`, `timestamp`
| `user_configs` | V2Ray/VLESS configs assigned to users | `id`, `user_id`, `node_id`, `plan_id`, `uuid`, `alter_id`, `protocol`, `status`, `created_at`, `expires_at`
| `usage` | Account-level consumption | `id`, `user_id`, `config_id`, `bytes_in`, `bytes_out`, `period_start`, `period_end`
| `audit_logs` | Trace admin/bot actions | `id`, `actor_type`, `actor_id`, `action`, `details`, `created_at`

> PostgreSQL is recommended for production; SQLite can power local development.

---

## 3. Repository Structure (Example)

```
/ctl-plane
  /app
    /api           # FastAPI routers (users, plans, nodes, payments)
    /core          # auth, config, scheduler, background jobs
    /models        # SQLAlchemy ORM models
    /schemas       # Pydantic DTOs
    /services      # business logic (payments, node orchestration)
    /workers       # Celery/RQ tasks (optional)
  /tests
  Dockerfile
  requirements.txt

/node-agent
  /agent
    main.py        # FastAPI/HTTP client, scheduler
    metrics.py     # system metrics collectors
    sync.py        # config pull/push logic
  Dockerfile
  requirements.txt

/telegram-bot
  bot.py
  keyboards.py
  scenes/         # conversation handlers per feature
  services/       # wrappers for control plane APIs
  utils/
  requirements.txt

/infra
  terraform/      # AWS/Azure/GCP provisioning
  ansible/        # optional playbooks for bare-metal nodes

/docs
  architecture.md
  api-reference.md
  runbooks/
```

---

## 4. Control Plane APIs

### Authentication
- `POST /api/v1/auth/token` – JWT issuance for node agents (client ID + secret) and admin dashboard.

### Node Management
- `POST /api/v1/nodes/register` – node agent registration, returns JWT.
- `POST /api/v1/nodes/heartbeat` – metrics payload (`cpu`, `mem`, `bandwidth`, `latency`).
- `GET /api/v1/nodes/{node_id}/configs` – retrieve updated configs for assignment.
- `POST /api/v1/nodes/{node_id}/configs/sync` – node acknowledges applied configs.

### User & Plan APIs
- `GET /api/v1/plans` – available plans filtered by region, constant/dynamic flag.
- `POST /api/v1/users/{user_id}/configs` – assign or reassign user to node.
- `POST /api/v1/payments` – create payment intent (manual), status `pending`.
- `POST /api/v1/payments/{id}/approve` – admin or auto accept; triggers full config delivery.
- `POST /api/v1/payments/{id}/reject` – marks payment as `rejected`, optionally bans user.

### Monitoring & Admin
- `GET /api/v1/dashboard/stats` – aggregated metrics (active users, pending payments, node health).
- `GET /api/v1/nodes/alerts` – nodes with high latency/load for proactive migration.

### Webhooks / Background Jobs
- APScheduler or Celery job runs every 5 minutes to:
  - Check pending payments exceeding 3 days → auto accept.
  - Evaluate node metrics → trigger migrations for dynamic users.

---

## 5. Node Agent Flow

### Agent Responsibilities
1. **Bootstrap**: read node secret, call `/nodes/register`, store JWT.
2. **Metrics**: every N seconds collect CPU, RAM, bandwidth (via `psutil`/`vnstat`) and send to `/nodes/heartbeat`.
3. **Config Sync**:
   - Poll `/nodes/{id}/configs` for new assignments.
   - Apply V2Ray JSON via local CLI (`xray api statsService`) or by updating config file and reloading the service.
   - Report success/failure back to control plane.
4. **Self-Healing**: detect local service failures, attempt restart, log incident.

### Implementation Outline
```python
# node-agent/agent/main.py
async def main():
    jwt = await register_node()
    while True:
        await push_metrics(jwt)
        await sync_configs(jwt)
        await asyncio.sleep(30)
```

---

## 6. Telegram Bot Flow

1. `/start` → language selection (English/Persian).
2. Offer plan categories (Constant IP vs Dynamic) and locations (local vs abroad).
3. Collect duration, data cap, concurrent devices.
4. Display price; upon confirmation, prompt for payment proof.
5. Create payment via control plane API; deliver temporary config (10% quota, 3 days).
6. Notify admin channel of pending review.
7. `/trial` command issues one-time 200 MB/1-day config if not previously used.
8. Admin commands (`/payments`, `/approve <id>`, `/reject <id>`, `/nodes`) to manage platform.

The bot talks to FastAPI via signed requests; user configs delivered as V2Ray links (`vmess://`, `vless://`).

---

## 7. Deployment Strategy

1. **Infrastructure**: Terraform provisions VPC, subnets, security groups, EC2/VMs (control plane + nodes). Add load balancer in front of control plane.
2. **Control Plane**: containerized FastAPI app deployed via Docker Compose, Kubernetes, or ECS. Use Gunicorn+Uvicorn workers.
3. **Database**: Managed PostgreSQL (RDS/Aurora) or cloud-managed SQLite for dev.
4. **Node Agent**: packaged as lightweight Docker image; installed on VMs or Kubernetes DaemonSet.
5. **Secrets**: Vault/SSM for Telegram tokens, JWT secrets, DB credentials.
6. **CI/CD (GitOps)**: GitHub Actions builds images, pushes to registry, updates Helm chart/manifests; ArgoCD or Flux applies cluster changes.

---

## 8. Health Monitoring & Migration Logic

- Store metrics in `node_metrics` table with TTL or partitioning.
- Define SLA thresholds (latency > 200ms, CPU > 85%, bandwidth > 90%).
- Scheduler identifies affected dynamic users and reassigns them to nodes within the same region tier (local vs abroad).
- Constant IP users stay pinned unless admin intervention.
- Use Prometheus + Grafana for monitoring; expose `/metrics` endpoint on control plane and node agent.

---

## 9. Future Scaling Plan

- **Auto-provision nodes**: integrate with AWS Auto Scaling Groups or Kubernetes Cluster Autoscaler to spin up new nodes when load exceeds threshold.
- **Global Load Balancing**: adopt Anycast IPs or DNS-based geolocation (Route 53 latency-based routing).
- **Billing Automation**: integrate Stripe/Zarinpal; add automatic invoice generation.
- **Advanced Analytics**: track churn, ARPU, node utilization; feed dashboards.
- **Zero-Downtime Config Deploys**: utilize V2Ray APIs for hot reload; maintain config audit trail.
- **Redundancy**: run multiple control plane replicas with shared database and Redis cache for rate limiting.

---

## 10. Summary Checklist

- [x] Control plane architecture with APIs and scheduler.
- [x] Node agent responsibilities and JWT auth model.
- [x] Telegram bot flow for sales, trials, and payments.
- [x] Database schema covering users, nodes, payments, configs, usage.
- [x] Deployment guidance and future scaling roadmap.

