from __future__ import annotations

from dataclasses import dataclass
from typing import List

from src.monitoring.models import MonitoringEvent
from src.monitoring.notifications.email_sender import EmailSender
from src.monitoring.notifications.formatter import AlertMessage
from src.monitoring.notifications.recipient_resolver import (
    RecipientResolver,
)


@dataclass(frozen=True)
class NotificationDeliveryResult:
    """
    Résultat d'une tentative d'envoi.
    """

    action_id: str
    recipient: str
    success: bool
    error: str | None = None


class NotificationService:
    """
    Orchestre l'envoi des messages correspondant
    aux événements de monitoring.

    Ce service :
    - ne calcule pas le niveau ;
    - ne choisit pas les destinataires ;
    - ne rédige pas le message.
    """

    def __init__(
        self,
        recipient_resolver: RecipientResolver,
        email_sender: EmailSender,
    ):
        self.recipient_resolver = recipient_resolver
        self.email_sender = email_sender

    def send_notifications(
        self,
        events: List[MonitoringEvent],
        messages: List[AlertMessage],
    ) -> List[NotificationDeliveryResult]:
        """
        Envoie chaque message aux destinataires configurés
        pour le niveau correspondant.
        """

        if len(events) != len(messages):
            raise ValueError(
                "Le nombre d'événements doit correspondre "
                "au nombre de messages."
            )

        delivery_results = []

        for event, message in zip(events, messages):
            recipients = self.recipient_resolver.resolve(
                escalation_level=event.current_level,
            )

            for recipient in recipients:
                try:
                    self.email_sender.send(
                        recipient=recipient,
                        message=message,
                    )

                    delivery_results.append(
                        NotificationDeliveryResult(
                            action_id=event.action.action_id,
                            recipient=recipient,
                            success=True,
                        )
                    )

                except Exception as exc:
                    delivery_results.append(
                        NotificationDeliveryResult(
                            action_id=event.action.action_id,
                            recipient=recipient,
                            success=False,
                            error=str(exc),
                        )
                    )

        return delivery_results