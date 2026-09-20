from pathlib import Path

from src.common.database import get_postgres_connection
from src.ingestion.postgres_audit_status_loader import (
    load_audit_status_snapshot,
)


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


def find_excel_file() -> Path:

    files = list(
        Path("data/incoming").glob("*.xlsx")
    )

    if len(files) != 1:
        raise ValueError(
            "data/incoming doit contenir exactement "
            "un fichier .xlsx."
        )

    return files[0]


if __name__ == "__main__":

    batch_id = get_latest_success_batch_id()

    excel_file = find_excel_file()

    count = load_audit_status_snapshot(
        excel_file=excel_file,
        batch_id=batch_id,
    )

    print(
        f"{count} statuts chargés "
        f"pour le batch {batch_id}"
    )