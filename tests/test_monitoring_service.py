from datetime import date

from src.monitoring.models import (
    ActionMonitoringInput,
    EscalationLevel,
)
from src.monitoring.service import CorrectiveActionMonitoringService


class FakeRepository:
    def get_actions_to_monitor(self):
        return [
            ActionMonitoringInput(
                action_id="1",
                date_debut=date(2026, 8, 1),
                is_closed=False,
                account_name="Compte A",
                action_text="Action corrective A",
                responsable="Responsable A",
                statut="En cours",
            ),
            ActionMonitoringInput(
                action_id="2",
                date_debut=date(2026, 6, 1),
                is_closed=False,
                account_name="Compte B",
                action_text="Action corrective B",
                responsable="Responsable B",
                statut="Ouvert",
            ),
        ]


class FakeAuditLogger:
    def __init__(self):
        self.logged_results = []
        self.previous_levels = {}

    def get_last_escalation_level(self, action_id):
        return self.previous_levels.get(action_id)

    def log_result(self, result):
        self.logged_results.append(result)

        self.previous_levels[result.action_id] = (
            result.niveau_escalade.value
            if result.niveau_escalade is not None
            else None
        )


def test_monitoring_service_returns_results_and_events():
    repository = FakeRepository()
    audit_logger = FakeAuditLogger()

    service = CorrectiveActionMonitoringService(
        repository=repository,
        audit_logger=audit_logger,
    )

    results, events = service.run(
        current_date=date(2026, 9, 20),
    )

    assert len(results) == 2
    assert len(events) == 2

    # Action 1
    assert results[0].action_id == "1"
    assert results[0].age_jours == 50
    assert results[0].niveau_escalade == EscalationLevel.ALERT

    # Action 2
    assert results[1].action_id == "2"
    assert results[1].age_jours == 111
    assert (
        results[1].niveau_escalade
        == EscalationLevel.MANAGEMENT_ESCALATION
    )

    # Vérification des événements
    assert events[0].action.action_id == "1"
    assert events[0].previous_level is None
    assert events[0].current_level == "alerte"

    assert events[1].action.action_id == "2"
    assert events[1].previous_level is None
    assert events[1].current_level == "escalade_management"

    # Les deux nouveaux niveaux ont été tracés
    assert len(audit_logger.logged_results) == 2


def test_same_escalation_level_does_not_create_new_event():
    repository = FakeRepository()
    audit_logger = FakeAuditLogger()

    service = CorrectiveActionMonitoringService(
        repository=repository,
        audit_logger=audit_logger,
    )

    _, first_events = service.run(
        current_date=date(2026, 9, 20),
    )

    _, second_events = service.run(
        current_date=date(2026, 9, 21),
    )

    # Première exécution :
    # aucun historique, donc 2 nouveaux événements.
    assert len(first_events) == 2

    # Deuxième exécution :
    # les âges changent, mais les niveaux restent identiques.
    assert len(second_events) == 0

    # Aucun nouveau log n'a été ajouté.
    assert len(audit_logger.logged_results) == 2


def test_change_of_escalation_level_creates_new_event():
    repository = FakeRepository()
    audit_logger = FakeAuditLogger()

    service = CorrectiveActionMonitoringService(
        repository=repository,
        audit_logger=audit_logger,
    )

    # Le 20 septembre :
    # action 1 = 50 jours -> alerte
    service.run(
        current_date=date(2026, 9, 20),
    )

    # On simule ensuite une date où l'action 1 dépasse 60 jours.
    _, events = service.run(
        current_date=date(2026, 10, 2),
    )

    action_1_events = [
        event
        for event in events
        if event.action.action_id == "1"
    ]

    assert len(action_1_events) == 1

    event = action_1_events[0]

    assert event.previous_level == "alerte"
    assert event.current_level == "critique"

    assert (
        event.result.niveau_escalade
        == EscalationLevel.CRITICAL
    )


def test_result_is_returned_even_when_no_new_event_is_created():
    repository = FakeRepository()
    audit_logger = FakeAuditLogger()

    service = CorrectiveActionMonitoringService(
        repository=repository,
        audit_logger=audit_logger,
    )

    service.run(
        current_date=date(2026, 9, 20),
    )

    results, events = service.run(
        current_date=date(2026, 9, 21),
    )

    # Toutes les actions sont toujours évaluées.
    assert len(results) == 2

    # Mais aucun nouveau changement de niveau.
    assert len(events) == 0

    assert results[0].age_jours == 51
    assert results[0].niveau_escalade == EscalationLevel.ALERT

    assert results[1].age_jours == 112
    assert (
        results[1].niveau_escalade
        == EscalationLevel.MANAGEMENT_ESCALATION
    )