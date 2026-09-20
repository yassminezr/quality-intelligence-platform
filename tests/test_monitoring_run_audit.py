from src.monitoring.run_audit import MonitoringRunLogger


class FakeCursor:
    def __init__(self):
        self.executed = []
        self.fetchone_result = (42,)

    def execute(self, query, params):
        self.executed.append(
            {
                "query": query,
                "params": params,
            }
        )

    def fetchone(self):
        return self.fetchone_result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()
        self.commit_count = 0

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.commit_count += 1


def test_start_run_returns_run_id():
    connection = FakeConnection()

    logger = MonitoringRunLogger(connection)

    run_id = logger.start_run()

    assert run_id == 42
    assert connection.commit_count == 1


def test_finish_success_updates_run():
    connection = FakeConnection()

    logger = MonitoringRunLogger(connection)

    logger.finish_success(
        run_id=42,
        actions_evaluated=50,
        events_detected=2,
        messages_prepared=2,
        emails_sent=2,
        emails_failed=0,
    )

    params = connection.cursor_instance.executed[0]["params"]

    assert params[1] == "success"
    assert params[2] == 50
    assert params[3] == 2
    assert params[4] == 2
    assert params[5] == 2
    assert params[6] == 0
    assert params[7] == 42

    assert connection.commit_count == 1


def test_finish_failed_updates_run():
    connection = FakeConnection()

    logger = MonitoringRunLogger(connection)

    logger.finish_failed(
        run_id=42,
        error_message="Database unavailable",
    )

    params = connection.cursor_instance.executed[0]["params"]

    assert params[1] == "failed"
    assert params[2] == "Database unavailable"
    assert params[3] == 42

    assert connection.commit_count == 1