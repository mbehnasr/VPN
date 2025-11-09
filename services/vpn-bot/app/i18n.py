from enum import Enum


class Language(str, Enum):
    EN = "en"
    FA = "fa"


MESSAGES = {
    "en": {
        "start": "Welcome! Choose your language to continue.",
        "language_selected": "Great, I'll use English.",
        "choose_location": "Select VPN location:",
        "choose_duration": "Select plan duration:",
        "choose_users": "How many users?",
        "choose_data": "Select data allowance:",
        "price_preview": "Current price: {price} {currency}. Confirm?",
        "payment_instructions": "Pay {amount} {currency}. Send payment proof (photo or text).",
        "payment_received": "Thanks! You'll receive a temporary plan shortly.",
        "trial_taken": "You already used your free trial.",
        "trial_granted": "Here is your free trial config:",
        "payment_blocked": "Payment invalid. You are banned.",
        "payment_pending": "Payment pending manual review. Temporary config:",
        "payment_accepted": "Payment accepted! Here is your full configuration:",
        "payment_rejected": "Payment rejected. Contact support.",
        "stats": "Users: {users}, Active Plans: {plans}, Pending Payments: {pending}",
    },
    "fa": {
        "start": "خوش آمدید! لطفاً زبان خود را انتخاب کنید.",
        "language_selected": "عالی، از این پس فارسی صحبت می‌کنم.",
        "choose_location": "سرور مورد نظر را انتخاب کنید:",
        "choose_duration": "مدت اشتراک را انتخاب کنید:",
        "choose_users": "تعداد کاربران:",
        "choose_data": "حجم مورد نیاز:",
        "price_preview": "قیمت فعلی: {price} {currency}. تایید می‌کنید؟",
        "payment_instructions": "مبلغ {amount} {currency} را پرداخت کرده و رسید را ارسال کنید.",
        "payment_received": "ممنون! به زودی پلن موقت دریافت می‌کنید.",
        "trial_taken": "شما قبلاً تست رایگان دریافت کرده‌اید.",
        "trial_granted": "پلن تست رایگان شما:",
        "payment_blocked": "رسید نامعتبر بود. شما مسدود شدید.",
        "payment_pending": "پرداخت در انتظار تایید است. پلن موقت:",
        "payment_accepted": "پرداخت تایید شد! کانفیگ کامل:",
        "payment_rejected": "پرداخت رد شد. با پشتیبانی تماس بگیرید.",
        "stats": "کاربران: {users}، پلن‌های فعال: {plans}، پرداخت‌های در انتظار: {pending}",
    },
}


def t(language: str, key: str, **kwargs) -> str:
    return MESSAGES.get(language, MESSAGES["en"]).get(key, key).format(**kwargs)
