from __future__ import annotations

from datetime import date
from typing import List, Tuple

from src.monitoring.models import (
    ActionMonitoringResult,
    MonitoringEvent,
)
from src.monitoring.rules import (
    calculate_action_age,
    classify_escalation_level,
)


class CorrectiveActionMonitoringService:
    """
    Orchestre le monitoring des actions correctives.
    """

    def __init__(self, repository, audit_logger):
        self.repository = repository
        self.audit_logger = audit_logger

    def run(
        self,
        current_date: date,
    ) -> Tuple[
        List[ActionMonitoringResult],
        List[MonitoringEvent],
    ]:
        """
        Exécute le monitoring.

        Retourne :
        - tous les résultats calculés ;
        - uniquement les changements de niveau détectés.
        """

        actions = self.repository.get_actions_to_monitor()

        results = []
        events = []

        for action in actions:
            age_days = calculate_action_age(
                action=action,
                current_date=current_date,
            )

            escalation_level = classify_escalation_level(
                age_days=age_days,
            )

            result = ActionMonitoringResult(
                action_id=action.action_id,
                age_jours=age_days,
                niveau_escalade=escalation_level,
                date_evaluation=current_date,
            )

            previous_level = (
                self.audit_logger.get_last_escalation_level(
                    action_id=action.action_id,
                )
            )

            current_level = (
                escalation_level.value
                if escalation_level is not None
                else None
            )

            if previous_level != current_level:
                self.audit_logger.log_result(result)

                event = MonitoringEvent(
                    action=action,
                    result=result,
                    previous_level=previous_level,
                    current_level=current_level,
                )

                events.append(event)

            results.append(result)

        return results, events