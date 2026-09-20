from __future__ import annotations

from typing import List

from src.monitoring.models import MonitoringEvent
from src.monitoring.notifications.formatter import (
    AlertMessage,
    build_alert_message,
)


class AlertPreparationService:
    """
    Prépare les messages correspondant aux nouveaux événements.

    Ce service ne réalise aucun envoi.
    """

    def prepare_messages(
        self,
        events: List[MonitoringEvent],
    ) -> List[AlertMessage]:
        """
        Génère un message pour chaque nouvel événement détecté.
        """

        messages = []

        for event in events:
            message = build_alert_message(
                action=event.action,
                result=event.result,
            )

            messages.append(message)

        return messages