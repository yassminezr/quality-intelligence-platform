from __future__ import annotations

import os

from src.monitoring.notifications.email_sender import SMTPEmailSender
from src.monitoring.notifications.recipient_resolver import RecipientResolver


def build_email_sender() -> SMTPEmailSender:
    return SMTPEmailSender(
        host=os.getenv("SMTP_HOST", ""),
        port=int(os.getenv("SMTP_PORT", "587")),
        username=os.getenv("SMTP_USERNAME", ""),
        password=os.getenv("SMTP_PASSWORD", ""),
        sender_email=os.getenv("SMTP_SENDER_EMAIL", ""),
        use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
    )


def build_recipient_resolver() -> RecipientResolver:
    recipients_by_level = {
        "alerte": [
            email
            for email in [
                os.getenv("QIP_RECIPIENT_ALERT"),
            ]
            if email
        ],
        "critique": [
            email
            for email in [
                os.getenv("QIP_RECIPIENT_CRITICAL"),
            ]
            if email
        ],
        "escalade_management": [
            email
            for email in [
                os.getenv("QIP_RECIPIENT_MANAGEMENT"),
            ]
            if email
        ],
    }

    return RecipientResolver(
        recipients_by_level=recipients_by_level,
    )