from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Protocol

from src.monitoring.notifications.formatter import AlertMessage


class EmailSender(Protocol):
    """
    Contrat générique pour l'envoi d'un email.
    """

    def send(
        self,
        recipient: str,
        message: AlertMessage,
    ) -> None:
        ...


class SMTPEmailSender:
    """
    Envoie les alertes via un serveur SMTP.

    Cette classe ne décide jamais du destinataire.
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        sender_email: str,
        use_tls: bool = True,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sender_email = sender_email
        self.use_tls = use_tls

    def send(
        self,
        recipient: str,
        message: AlertMessage,
    ) -> None:
        email = EmailMessage()

        email["From"] = self.sender_email
        email["To"] = recipient
        email["Subject"] = message.subject

        email.set_content(message.body)

        with smtplib.SMTP(
            host=self.host,
            port=self.port,
        ) as smtp:
            if self.use_tls:
                smtp.starttls()

            smtp.login(
                self.username,
                self.password,
            )

            smtp.send_message(email)