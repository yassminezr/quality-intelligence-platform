from datetime import date

from src.monitoring.models import (
    ActionMonitoringInput,
    ActionMonitoringResult,
    EscalationLevel,
)
from src.monitoring.notifications.formatter import build_alert_message


def test_build_alert_message():
    action = ActionMonitoringInput(
        action_id="1",
        date_debut=date(2026, 7, 15),
        is_closed=False,
        account_name="Min. Intérieur",
        action_text="Formaliser le suivi des enjeux.",
        responsable="Mohamed",
        statut="En cours",
    )

    result = ActionMonitoringResult(
        action_id="1",
        age_jours=67,
        niveau_escalade=EscalationLevel.CRITICAL,
        date_evaluation=date(2026, 9, 20),
    )

    message = build_alert_message(
        action=action,
        result=result,
    )

    assert "Critique" in message.subject
    assert "Min. Intérieur" in message.subject

    assert "67 jours" in message.body
    assert "Mohamed" in message.body
    assert "Formaliser le suivi des enjeux." in message.body


def test_missing_values_are_not_invented():
    action = ActionMonitoringInput(
        action_id="2",
        date_debut=None,
        is_closed=False,
    )

    result = ActionMonitoringResult(
        action_id="2",
        age_jours=None,
        niveau_escalade=None,
        date_evaluation=date(2026, 9, 20),
    )

    message = build_alert_message(
        action=action,
        result=result,
    )

    assert "Non renseigné" in message.body
    assert "Non calculable" in message.body
    assert "Non déterminé" in message.body