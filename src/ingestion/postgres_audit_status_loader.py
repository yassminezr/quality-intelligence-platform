from pathlib import Path

from src.common.database import get_postgres_connection
from src.ingestion.audit_status_extractor import (
    extract_audit_statuses,
)


def load_audit_status_snapshot(
    excel_file: Path,
    batch_id: str,
) -> int:

    statuses = extract_audit_statuses(excel_file)

    with get_postgres_connection() as conn:
        with conn.cursor() as cur:

            # Vérifier que tous les comptes existent dans le Core
            cur.execute(
                """
                SELECT account_name
                FROM core.account
                """
            )

            core_accounts = {
                row[0]
                for row in cur.fetchall()
            }

            extracted_accounts = set(
                statuses["account_name"]
            )

            missing_accounts = (
                extracted_accounts - core_accounts
            )

            if missing_accounts:
                raise ValueError(
                    "Comptes absents de core.account : "
                    + ", ".join(
                        sorted(missing_accounts)
                    )
                )

            # Idempotence pour le même batch
            cur.execute(
                """
                DELETE FROM staging.audit_status_snapshot
                WHERE batch_id = %s
                """,
                (batch_id,),
            )

            for row in statuses.itertuples(
                index=False
            ):
                cur.execute(
                    """
                    INSERT INTO staging.audit_status_snapshot (
                        batch_id,
                        source_file,
                        account_name,
                        source_status,
                        validated_status
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        batch_id,
                        Path(excel_file).name,
                        row.account_name,
                        row.source_status,
                        row.validated_status,
                    ),
                )

        conn.commit()

    return len(statuses)