from __future__ import annotations

import argparse

from src.common.database import get_postgres_connection


def get_latest_success_batch_id() -> str:
    with get_postgres_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT batch_id
                FROM metadata.ingestion_batch
                WHERE status = 'SUCCESS'
                ORDER BY ingestion_timestamp DESC
                LIMIT 1
                """
            )

            row = cur.fetchone()

            if row is None:
                raise ValueError(
                    "Aucun batch SUCCESS trouvé."
                )

            return str(row[0])


def load_audit_validations(
    batch_id: str,
) -> dict[str, int]:

    updated = 0
    unchanged = 0

    with get_postgres_connection() as conn:
        with conn.cursor() as cur:

            # -----------------------------------------
            # Campagne associée au batch
            # -----------------------------------------

            cur.execute(
                """
                SELECT campaign
                FROM metadata.ingestion_batch
                WHERE batch_id = %s
                """,
                (batch_id,),
            )

            row = cur.fetchone()

            if row is None:
                raise ValueError(
                    f"Batch introuvable : {batch_id}"
                )

            campaign_name = row[0]

            # -----------------------------------------
            # Statuts officiels du snapshot
            # -----------------------------------------

            cur.execute(
                """
                SELECT
                    account_name,
                    source_status,
                    validated_status
                FROM staging.audit_status_snapshot
                WHERE batch_id = %s
                ORDER BY account_name
                """,
                (batch_id,),
            )

            statuses = cur.fetchall()

            if not statuses:
                raise ValueError(
                    "Aucun statut trouvé dans "
                    "staging.audit_status_snapshot "
                    f"pour le batch {batch_id}"
                )

            for (
                account_name,
                source_status,
                validated_status,
            ) in statuses:

                # -----------------------------------------
                # Audit du compte pour la campagne
                # -----------------------------------------

                cur.execute(
                    """
                    SELECT
                        a.audit_id,
                        a.current_proposed_status,
                        a.current_validated_status
                    FROM core.audit a

                    JOIN core.account acc
                        ON acc.account_id = a.account_id

                    JOIN core.campaign c
                        ON c.campaign_id = a.campaign_id

                    WHERE
                        acc.account_name = %s
                        AND c.campaign_name = %s
                    """,
                    (
                        account_name,
                        campaign_name,
                    ),
                )

                audit = cur.fetchone()

                if audit is None:
                    raise ValueError(
                        "Audit introuvable pour "
                        f"{account_name} / {campaign_name}"
                    )

                (
                    audit_id,
                    proposed_status,
                    current_validated_status,
                ) = audit

                # -----------------------------------------
                # Aucun changement
                # -----------------------------------------

                if (
                    current_validated_status
                    == validated_status
                ):
                    unchanged += 1
                    continue

                # -----------------------------------------
                # Mise à jour du statut courant
                # -----------------------------------------

                cur.execute(
                    """
                    UPDATE core.audit
                    SET
                        current_validated_status = %s,
                        status_last_updated_at = NOW(),
                        updated_at = NOW()
                    WHERE audit_id = %s
                    """,
                    (
                        validated_status,
                        audit_id,
                    ),
                )

                # -----------------------------------------
                # Historique
                # -----------------------------------------
                #
                # validation_date reste NULL car le fichier
                # ne fournit pas la date réelle de validation
                # humaine.
                #
                # created_at enregistre automatiquement
                # le moment où le pipeline a observé
                # le changement.
                # -----------------------------------------

                cur.execute(
                    """
                    INSERT INTO core.audit_status_validation (
                        audit_id,
                        proposed_status,
                        validated_status,
                        validation_date,
                        validated_by
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        NULL,
                        %s
                    )
                    """,
                    (
                        audit_id,
                        proposed_status,
                        validated_status,
                        "DASHBOARD AUDITS",
                    ),
                )

                updated += 1

        conn.commit()

    return {
        "updated": updated,
        "unchanged": unchanged,
        "total": updated + unchanged,
    }


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--batch-id",
        required=False,
    )

    args = parser.parse_args()

    batch_id = (
        args.batch_id
        if args.batch_id
        else get_latest_success_batch_id()
    )

    result = load_audit_validations(
        batch_id=batch_id
    )

    print(
        f"Batch : {batch_id}"
    )

    print(
        f"Statuts traités : {result['total']}"
    )

    print(
        f"Statuts modifiés : {result['updated']}"
    )

    print(
        f"Statuts inchangés : {result['unchanged']}"
    )