from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

from app.config import get_settings


Base = declarative_base()
settings = get_settings()
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(150))
    language = Column(String(5), default="en")
    banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    payments = relationship("Payment", back_populates="user")
    usages = relationship("Usage", back_populates="user")


class VPNPlan(Base):
    __tablename__ = "vpn_plans"

    id = Column(Integer, primary_key=True)
    location = Column(String(50), nullable=False)
    duration_months = Column(Integer, nullable=False)
    max_users = Column(Integer, nullable=False)
    data_gib = Column(Integer, nullable=False)
    price_eur = Column(Float, nullable=False)
    active = Column(Boolean, default=True)


class PaymentStatusEnum(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    auto_accepted = "auto_accepted"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("vpn_plans.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(SAEnum(PaymentStatusEnum), default=PaymentStatusEnum.pending)
    evidence_file_id = Column(String(150))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="payments")
    plan = relationship("VPNPlan")
    logs = relationship("Log", back_populates="payment")


class Usage(Base):
    __tablename__ = "usage"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    config_payload = Column(Text, nullable=False)
    quota_mb = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_trial = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="usages")
    payment = relationship("Payment")


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100))
    details = Column(Text)
    created_at = Column(DateTime, default=func.now())

    payment = relationship("Payment", back_populates="logs")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
