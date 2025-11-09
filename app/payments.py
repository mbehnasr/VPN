from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import Log, Payment, PaymentStatusEnum, Usage
from app.vpn_utils import build_usage_record, create_temp_plan

settings = get_settings()


def grant_temp_plan(session: Session, payment: Payment, server: dict) -> Usage:
    temp_mb = create_temp_plan(payment.plan.data_gib)
    config, quota, expires = build_usage_record(server, temp_mb, duration_days=3, is_trial=True)
    usage = Usage(
        user_id=payment.user_id,
        payment_id=payment.id,
        config_payload=config,
        quota_mb=quota,
        expires_at=expires,
        is_trial=True,
    )
    session.add(usage)
    session.add(
        Log(
            payment_id=payment.id,
            user_id=payment.user_id,
            action="temp_plan",
            details=f"{temp_mb} MB granted",
        )
    )
    return usage


def grant_full_plan(session: Session, payment: Payment, server: dict) -> Usage:
    config, quota, expires = build_usage_record(
        server,
        data_gib=payment.plan.data_gib,
        duration_days=payment.plan.duration_months * 30,
        is_trial=False,
    )
    usage = Usage(
        user_id=payment.user_id,
        payment_id=payment.id,
        config_payload=config,
        quota_mb=quota,
        expires_at=expires,
    )
    session.add(usage)
    session.add(Log(payment_id=payment.id, user_id=payment.user_id, action="plan_activated"))
    return usage


def auto_accept_overdue(session: Session) -> None:
    threshold = datetime.utcnow() - timedelta(days=settings.auto_accept_days)
    overdue = (
        session.query(Payment)
        .filter(Payment.status == PaymentStatusEnum.pending, Payment.created_at <= threshold)
        .all()
    )
    for payment in overdue:
        payment.status = PaymentStatusEnum.auto_accepted
        grant_full_plan(session, payment, server=_choose_server(payment.plan.location))
        session.add(Log(payment_id=payment.id, action="auto_accept"))


def mark_invalid_payment(session: Session, payment: Payment, reason: str) -> None:
    payment.status = PaymentStatusEnum.rejected
    payment.user.banned = True
    session.add(
        Log(
            payment_id=payment.id,
            user_id=payment.user_id,
            action="ban",
            details=reason,
        )
    )


def _choose_server(location: str) -> dict:
    mapping = {
        "france": {"host": "fr.example.com", "port": 443, "alter_id": 0, "network": "tcp", "name": "France"},
        "germany": {"host": "de.example.com", "port": 443, "alter_id": 0, "network": "tcp", "name": "Germany"},
        "singapore": {"host": "sg.example.com", "port": 443, "alter_id": 0, "network": "tcp", "name": "Singapore"},
    }
    return mapping[location.lower()]
