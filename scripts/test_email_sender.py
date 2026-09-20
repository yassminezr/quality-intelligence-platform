from src.monitoring.notifications.formatter import AlertMessage
from src.monitoring.notifications.notification_config import (
    build_email_sender,
)


def main():
    sender = build_email_sender()

    message = AlertMessage(
        subject="[QIP] Test notification email",
        body=(
            "Ceci est un test d'envoi email "
            "depuis Quality Intelligence Platform."
        ),
    )

    sender.send(
        recipient=sender.sender_email,
        message=message,
    )

    print("Email de test envoyé.")


if __name__ == "__main__":
    main()