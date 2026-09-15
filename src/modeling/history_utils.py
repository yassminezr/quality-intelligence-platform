from __future__ import annotations


def values_changed(
    current_values: tuple,
    new_values: tuple,
) -> bool:
    """
    Compare l'état actuel avec
    les nouvelles valeurs du batch.
    """

    return current_values != new_values


def save_evaluation_version(
    cursor,
    evaluation_id: int,
    batch_id: str,
    score_maturite,
    niveau_maturite,
    constat_auditeur,
) -> None:
    """
    Enregistre une version d'évaluation.
    """

    cursor.execute(
        """
        INSERT INTO core.evaluation_history (
            evaluation_id,
            batch_id,
            score_maturite,
            niveau_maturite,
            constat_auditeur,
            valid_from
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            NOW()
        )

        ON CONFLICT (
            evaluation_id,
            batch_id
        )

        DO NOTHING;
        """,
        (
            evaluation_id,
            batch_id,
            score_maturite,
            niveau_maturite,
            constat_auditeur,
        ),
    )


def save_action_status_version(
    cursor,
    action_id: int,
    batch_id: str,
    status,
) -> None:
    """
    Enregistre une version du statut
    d'une action corrective.
    """

    cursor.execute(
        """
        INSERT INTO
            core.corrective_action_status_history (
                action_id,
                batch_id,
                status,
                changed_at
            )

        VALUES (
            %s,
            %s,
            %s,
            NOW()
        )

        ON CONFLICT DO NOTHING;
        """,
        (
            action_id,
            batch_id,
            status,
        ),
    )