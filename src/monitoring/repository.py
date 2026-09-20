from __future__ import annotations

from typing import List

import psycopg2

from src.monitoring.models import ActionMonitoringInput


class CorrectiveActionRepository:
    """
    Accès aux actions correctives stockées dans PostgreSQL.
    """

    def __init__(self, connection):
        self.connection = connection

    def get_actions_to_monitor(self) -> List[ActionMonitoringInput]:
        """
        Retourne les actions correctives présentes dans le mart analytics.

        Le repository lit les données mais ne prend aucune décision métier.
        """

        query = """
            SELECT
                action_id,
                date_debut,
                is_closed,
                age_jours,
                account_name,
                action_text,
                responsable,
                statut
            FROM analytics.mart_corrective_actions
            ORDER BY action_id;
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        actions = []

        for row in rows:
            (
                action_id,
                date_debut,
                is_closed,
                age_jours,
                account_name,
                action_text,
                responsable,
                statut,
            ) = row

            actions.append(
                ActionMonitoringInput(
                    action_id=str(action_id),
                    date_debut=date_debut,
                    is_closed=is_closed,
                    frozen_age_days=age_jours if is_closed else None,
                    account_name=account_name,
                    action_text=action_text,
                    responsable=responsable,
                    statut=statut,
                )
            )

        return actions