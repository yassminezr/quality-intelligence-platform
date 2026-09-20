from datetime import date

from src.monitoring.models import (
    ActionMonitoringInput,
    ActionMonitoringResult,
    EscalationLevel,
    MonitoringEvent,
)
from src.monitoring.notifications.service import AlertPreparationService


def test_prepare_messages_from_events():
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

    event = MonitoringEvent(
        action=action,
        result=result,
        previous_level="alerte",
        current_level="critique",
    )

    service = AlertPreparationService()

    messages = service.prepare_messages(
        events=[event],
    )

    assert len(messages) == 1

    assert "Critique" in messages[0].subject
    assert "Min. Intérieur" in messages[0].subject

    assert "67 jours" in messages[0].body
    assert "Mohamed" in messages[0].body


def test_no_events_produce_no_messages():
    service = AlertPreparationService()

    messages = service.prepare_messages(
        events=[],
    )

    assert messages == []