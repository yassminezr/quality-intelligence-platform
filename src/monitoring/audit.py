from __future__ import annotations

from datetime import datetime, timezone

from src.monitoring.models import ActionMonitoringResult


class MonitoringAuditLogger:
    """
    Persiste les résultats du moteur de monitoring
    dans la table monitoring.action_monitoring_log.
    """

    def __init__(self, connection):
        self.connection = connection

    def log_result(self, result: ActionMonitoringResult) -> None:
        """
        Enregistre un résultat de monitoring.
        """

        query = """
            INSERT INTO monitoring.action_monitoring_log (
                action_id,
                age_jours,
                niveau_escalade,
                monitored_at
            )
            VALUES (%s, %s, %s, %s);
        """

        monitored_at = datetime.now(timezone.utc)

        escalation_value = (
            result.niveau_escalade.value
            if result.niveau_escalade is not None
            else None
        )

        with self.connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    int(result.action_id),
                    result.age_jours,
                    escalation_value,
                    monitored_at,
                ),
            )

        self.connection.commit()

    def get_last_escalation_level(
        self,
        action_id: str,
    ) -> str | None:
        """
        Retourne le dernier niveau d'escalade enregistré
        pour une action corrective.

        Retourne None si l'action n'a jamais encore été monitorée.
        """

        query = """
            SELECT niveau_escalade
            FROM monitoring.action_monitoring_log
            WHERE action_id = %s
            ORDER BY monitored_at DESC, monitoring_log_id DESC
            LIMIT 1;
        """

        with self.connection.cursor() as cursor:
            cursor.execute(
                query,
                (int(action_id),),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return row[0]