from datetime import date

from src.monitoring.audit import MonitoringAuditLogger
from src.monitoring.models import (
    ActionMonitoringResult,
    EscalationLevel,
)


class FakeCursor:
    def __init__(self):
        self.executed_query = None
        self.executed_params = None

    def execute(self, query, params):
        self.executed_query = query
        self.executed_params = params

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()
        self.committed = False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.committed = True


def test_log_result_inserts_monitoring_decision():
    connection = FakeConnection()

    logger = MonitoringAuditLogger(connection)

    result = ActionMonitoringResult(
        action_id="1",
        age_jours=67,
        niveau_escalade=EscalationLevel.CRITICAL,
        date_evaluation=date(2026, 9, 20),
    )

    logger.log_result(result)

    params = connection.cursor_instance.executed_params

    assert params[0] == 1
    assert params[1] == 67
    assert params[2] == "critique"

    assert connection.committed is True