from __future__ import annotations

import argparse

from src.common.database import (
    get_postgres_connection,
)
from src.modeling.history_utils import (
    save_action_status_version,
    save_evaluation_version,
)


def backfill_history(
    batch_id: str,
) -> None:

    connection = (
        get_postgres_connection()
    )

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    evaluation_id,
                    score_maturite,
                    niveau_maturite,
                    constat_auditeur
                FROM core.evaluation;
                """
            )

            evaluations = (
                cursor.fetchall()
            )

            for (
                evaluation_id,
                score,
                niveau,
                constat,
            ) in evaluations:

                save_evaluation_version(
                    cursor=cursor,
                    evaluation_id=evaluation_id,
                    batch_id=batch_id,
                    score_maturite=score,
                    niveau_maturite=niveau,
                    constat_auditeur=constat,
                )

            cursor.execute(
                """
                SELECT
                    action_id,
                    statut
                FROM core.corrective_action;
                """
            )

            actions = cursor.fetchall()

            for (
                action_id,
                status,
            ) in actions:

                save_action_status_version(
                    cursor=cursor,
                    action_id=action_id,
                    batch_id=batch_id,
                    status=status,
                )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    print(
        "History backfill completed."
    )

    print(
        "Evaluations:",
        len(evaluations),
    )

    print(
        "Actions:",
        len(actions),
    )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--batch-id",
        required=True,
    )

    args = parser.parse_args()

    backfill_history(
        batch_id=args.batch_id
    )


if __name__ == "__main__":
    main()