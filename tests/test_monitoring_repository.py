from datetime import date

from src.monitoring.repository import CorrectiveActionRepository


class FakeCursor:
    def execute(self, query):
        self.query = query

    def fetchall(self):
        return [
            (
                1,
                date(2026, 7, 15),
                False,
                66,
                "Min. Intérieur",
                "Formaliser le suivi",
                "Mohamed",
                "En cours",
            ),
            (
                2,
                date(2026, 6, 1),
                True,
                45,
                "Compte B",
                "Mettre à jour le processus",
                "Sara",
                "Clôturé",
            ),
        ]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class FakeConnection:
    def cursor(self):
        return FakeCursor()


def test_repository_returns_monitoring_inputs():
    repository = CorrectiveActionRepository(FakeConnection())

    actions = repository.get_actions_to_monitor()

    assert len(actions) == 2

    assert actions[0].action_id == "1"
    assert actions[0].date_debut == date(2026, 7, 15)
    assert actions[0].is_closed is False
    assert actions[0].frozen_age_days is None

    assert actions[0].account_name == "Min. Intérieur"
    assert actions[0].responsable == "Mohamed"
    assert actions[0].action_text == "Formaliser le suivi"

    assert actions[1].action_id == "2"
    assert actions[1].is_closed is True
    assert actions[1].frozen_age_days == 45