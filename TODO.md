# Project TODOs

## Plan Data & Pricing
- [ ] Seed `vpn_plans` table with production-ready combinations (location, duration, users, data, price).
- [ ] Add currency helper utilities to support dynamic pricing and future multi-currency support.

## Bot User Experience
- [ ] Replace `_mock_server` with real server metadata sourced from the database.
- [ ] Expand localization coverage and improve reply keyboards or inline buttons for better UX.
- [ ] Persist in-progress purchases to allow resuming flows after /start.

## Payment Workflow
- [ ] Add admin commands (`/accept`, `/reject`) to review payments from Telegram.
- [ ] Schedule `auto_accept_overdue` via APScheduler or FastAPI background task.
- [ ] Integrate Stripe sandbox endpoints and webhook handlers; store payment processor IDs.
- [ ] Integrate Zarinpal sandbox endpoints and verification flow.

## Security & Validation
- [ ] Gate admin HTTP endpoints with API keys or JWT-based auth.
- [ ] Implement rate limiting for trial requests and duplicate payment proofs.

## Database & Schema Management
- [ ] Add Alembic migrations; generate baseline migration for current models.
- [ ] Create `servers` table to map location → host/port/network; update plan linkage.

## V2Ray Provisioning
- [ ] Implement remote provisioning script/API call to push configs to V2Ray servers.
- [ ] Track config lifecycle (activation, revocation) and automate clean-up.

## Testing
- [ ] Write unit tests for utilities (`create_temp_plan`, `grant_temp_plan`, conversation flow).
- [ ] Add integration tests for FastAPI admin endpoints using TestClient.

## Admin Dashboard
- [ ] Expand FastAPI admin routes with pagination, filtering, and mutations.
- [ ] Decide on frontend stack (e.g., Next.js) and define API contracts for dashboard.
- [ ] Establish admin authentication (OAuth2, Magic Link, etc.) for web dashboard.

## Deployment & Operations
- [ ] Transition Telegram bot to webhook mode served via FastAPI.
- [ ] Containerize the application with Docker and set up CI pipeline.
- [ ] Create systemd timer or cron for auto-accept job and regular database backups.
- [ ] Configure structured logging and integrate Sentry or OpenTelemetry.
- [ ] Expose Prometheus metrics for FastAPI and bot activity.
- [ ] Plan migration path to PostgreSQL and introduce Redis for caching/rate limiting.
