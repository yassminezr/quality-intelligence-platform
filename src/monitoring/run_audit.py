from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


class MonitoringRunLogger:
    """
    Historise les exécutions globales du monitoring.
    """

    def __init__(self, connection):
        self.connection = connection

    def start_run(self) -> int:
        """
        Crée un nouveau run avec le statut 'running'
        et retourne son run_id.
        """

        query = """
            INSERT INTO monitoring.monitoring_run_log (
                started_at,
                status
            )
            VALUES (%s, %s)
            RETURNING run_id;
        """

        started_at = datetime.now(timezone.utc)

        with self.connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    started_at,
                    "running",
                ),
            )

            run_id = cursor.fetchone()[0]

        self.connection.commit()

        return run_id

    def finish_success(
        self,
        run_id: int,
        actions_evaluated: int,
        events_detected: int,
        messages_prepared: int,
        emails_sent: int,
        emails_failed: int,
    ) -> None:
        """
        Termine un run avec le statut 'success'.
        """

        query = """
            UPDATE monitoring.monitoring_run_log
            SET
                finished_at = %s,
                status = %s,
                actions_evaluated = %s,
                events_detected = %s,
                messages_prepared = %s,
                emails_sent = %s,
                emails_failed = %s,
                error_message = NULL
            WHERE run_id = %s;
        """

        finished_at = datetime.now(timezone.utc)

        with self.connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    finished_at,
                    "success",
                    actions_evaluated,
                    events_detected,
                    messages_prepared,
                    emails_sent,
                    emails_failed,
                    run_id,
                ),
            )

        self.connection.commit()

    def finish_failed(
        self,
        run_id: int,
        error_message: Optional[str],
    ) -> None:
        """
        Termine un run avec le statut 'failed'.
        """

        query = """
            UPDATE monitoring.monitoring_run_log
            SET
                finished_at = %s,
                status = %s,
                error_message = %s
            WHERE run_id = %s;
        """

        finished_at = datetime.now(timezone.utc)

        with self.connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    finished_at,
                    "failed",
                    error_message,
                    run_id,
                ),
            )

        self.connection.commit()