from __future__ import annotations

from datetime import datetime, timedelta

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app import logging_conf
from app.config import get_settings
from app.db import Payment, PaymentStatusEnum, User, VPNPlan, Usage, session_scope
from app.i18n import t
from app.payments import grant_temp_plan

settings = get_settings()
logger = logging_conf.get_logger(__name__)

LANGUAGE, LOCATION, DURATION, USERS, DATA, PAYMENT_PROOF = range(6)


def _language_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["English", "فارسی"]], one_time_keyboard=True, resize_keyboard=True)


def _location_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["France", "Germany"], ["Singapore"]], resize_keyboard=True)


def _duration_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["1 month", "2 months"]], resize_keyboard=True)


def _users_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["1", "2", "3"]], resize_keyboard=True)


def _data_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["10 GiB", "20 GiB"], ["50 GiB"]], resize_keyboard=True)


def _confirm_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["Confirm", "Cancel"]], resize_keyboard=True)


def _choice_to_language(choice: str) -> str:
    return "fa" if "فار" in choice else "en"


def _get_plan(filters: dict) -> VPNPlan | None:
    with session_scope() as session:
        return (
            session.query(VPNPlan)
            .filter_by(
                location=filters["location"],
                duration_months=filters["duration"],
                max_users=filters["users"],
                data_gib=filters["data_gib"],
            )
            .first()
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    with session_scope() as session:
        db_user = session.query(User).filter_by(telegram_id=user.id).first()
        if not db_user:
            session.add(User(telegram_id=user.id, username=user.username))
    await update.message.reply_text(t("en", "start"), reply_markup=_language_keyboard())
    return LANGUAGE


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = _choice_to_language(update.message.text.lower())
    context.user_data["language"] = language
    await update.message.reply_text(t(language, "language_selected"), reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(t(language, "choose_location"), reply_markup=_location_keyboard())
    return LOCATION


async def choose_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["location"] = update.message.text.lower()
    language = context.user_data["language"]
    await update.message.reply_text(t(language, "choose_duration"), reply_markup=_duration_keyboard())
    return DURATION


async def choose_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    duration = 1 if "1" in update.message.text else 2
    context.user_data["duration"] = duration
    language = context.user_data["language"]
    await update.message.reply_text(t(language, "choose_users"), reply_markup=_users_keyboard())
    return USERS


async def choose_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["users"] = int(update.message.text)
    language = context.user_data["language"]
    await update.message.reply_text(t(language, "choose_data"), reply_markup=_data_keyboard())
    return DATA


async def choose_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data["language"]
    context.user_data["data_gib"] = int(update.message.text.split()[0])
    plan = _get_plan(context.user_data)
    if not plan:
        await update.message.reply_text("Plan not available. Please try again.")
        return ConversationHandler.END
    context.user_data["plan_id"] = plan.id
    await update.message.reply_text(
        t(language, "price_preview", price=plan.price_eur, currency=settings.base_currency),
        reply_markup=_confirm_keyboard(),
    )
    return PAYMENT_PROOF


async def payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get("language", "en")

    if update.message.text and update.message.text.lower() == "cancel":
        await update.message.reply_text("Cancelled.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    evidence_id = None
    if update.message.photo:
        evidence_id = update.message.photo[-1].file_id
    elif update.message.document:
        evidence_id = update.message.document.file_id
    else:
        evidence_id = update.message.text

    user_id = update.effective_user.id
    with session_scope() as session:
        db_user = session.query(User).filter_by(telegram_id=user_id).first()
        plan = session.get(VPNPlan, context.user_data["plan_id"])
        payment = Payment(
            user_id=db_user.id,
            plan_id=plan.id,
            amount=plan.price_eur,
            evidence_file_id=evidence_id,
            expires_at=datetime.utcnow() + timedelta(days=settings.auto_accept_days),
        )
        session.add(payment)
        usage = grant_temp_plan(session, payment, _mock_server(plan.location))
        message = t(language, "payment_pending") + "\n" + usage.config_payload

    await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def _mock_server(location: str) -> dict:
    mapping = {
        "france": {"host": "fr.example.com", "port": 443, "alter_id": 0, "network": "tcp", "name": "France"},
        "germany": {"host": "de.example.com", "port": 443, "alter_id": 0, "network": "tcp", "name": "Germany"},
        "singapore": {"host": "sg.example.com", "port": 443, "alter_id": 0, "network": "tcp", "name": "Singapore"},
    }
    return mapping[location]


async def grant_trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get("language", "en")
    user_id = update.effective_user.id
    with session_scope() as session:
        db_user = session.query(User).filter_by(telegram_id=user_id).first()
        if session.query(Usage).filter_by(user_id=db_user.id, is_trial=True).count() > 0:
            await update.message.reply_text(t(language, "trial_taken"))
            return
        config_payload = "trial-config"
        usage = Usage(
            user_id=db_user.id,
            config_payload=config_payload,
            quota_mb=settings.trial_quota_mb,
            expires_at=datetime.utcnow() + timedelta(days=settings.trial_duration_days),
            is_trial=True,
        )
        session.add(usage)
    await update.message.reply_text(t(language, "trial_granted") + "\n" + "trial-config")


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in settings.admin_chat_ids:
        return
    language = context.user_data.get("language", "en")
    with session_scope() as session:
        users = session.query(User).count()
        plans = session.query(Usage).count()
        pending = session.query(Payment).filter_by(status=PaymentStatusEnum.pending).count()
    await update.message.reply_text(t(language, "stats", users=users, plans=plans, pending=pending))


def build_bot():
    application = ApplicationBuilder().token(settings.telegram_token).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_language)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_location)],
            DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_duration)],
            USERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_users)],
            DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_data)],
            PAYMENT_PROOF: [
                MessageHandler(
                    (filters.TEXT | filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND,
                    payment_proof,
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", lambda *_: ConversationHandler.END)],
    )
    application.add_handler(conv)
    application.add_handler(CommandHandler("trial", grant_trial))
    application.add_handler(CommandHandler("stats", admin_stats))
    return application
