from __future__ import annotations

from threading import Thread

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.bot import build_bot
from app.db import Payment, Usage, User, init_db, session_scope
from app.logging_conf import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    init_db()

    app = FastAPI(title="VPN Sales Bot API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/admin/users")
    async def list_users():
        with session_scope() as session:
            users = session.query(User).all()
            return [
                {"id": u.id, "telegram_id": u.telegram_id, "banned": u.banned, "created_at": u.created_at}
                for u in users
            ]

    @app.get("/admin/payments")
    async def list_payments():
        with session_scope() as session:
            payments = session.query(Payment).all()
            return [
                {
                    "id": p.id,
                    "status": p.status.value,
                    "amount": p.amount,
                    "user_id": p.user_id,
                    "plan_id": p.plan_id,
                    "created_at": p.created_at,
                }
                for p in payments
            ]

    @app.get("/admin/usages")
    async def list_usages():
        with session_scope() as session:
            usages = session.query(Usage).all()
            return [
                {
                    "id": u.id,
                    "user_id": u.user_id,
                    "quota_mb": u.quota_mb,
                    "expires_at": u.expires_at,
                    "is_trial": u.is_trial,
                }
                for u in usages
            ]

    return app


def run_bot() -> None:
    application = build_bot()
    application.run_polling(drop_pending_updates=True)


def main() -> None:
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    uvicorn.run(create_app(), host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
