from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.common.database import (
    get_postgres_connection,
)


def load_dq_issues(
    csv_path: Path,
    batch_id: str,
) -> int:
    """
    Charge dq_issues.csv dans quality.dq_issues.

    Le chargement est idempotent :
    les anciennes anomalies du batch
    sont supprimées avant réinsertion.
    """

    if not csv_path.exists():
        raise FileNotFoundError(
            f"DQ issues file not found: {csv_path}"
        )

    dataframe = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
    )

    expected_columns = [
        "rule_id",
        "severity",
        "message",
        "source_file",
        "source_sheet",
        "source_row_number",
    ]

    missing_columns = [
        column
        for column in expected_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing columns in dq_issues.csv: "
            + ", ".join(missing_columns)
        )

    dataframe = dataframe[
        expected_columns
    ].copy()

    dataframe = dataframe.astype(
        object
    ).where(
        pd.notna(dataframe),
        None,
    )

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            # Idempotence :
            # supprimer les anciennes anomalies
            # correspondant à ce batch.
            cursor.execute(
                """
                DELETE FROM quality.dq_issues
                WHERE batch_id = %s;
                """,
                (batch_id,),
            )

            insert_sql = """
                INSERT INTO quality.dq_issues (
                    batch_id,
                    rule_id,
                    severity,
                    message,
                    source_file,
                    source_sheet,
                    source_row_number
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                );
            """

            for row in dataframe.itertuples(
                index=False,
                name=None,
            ):
                cursor.execute(
                    insert_sql,
                    (
                        batch_id,
                        *row,
                    ),
                )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return len(dataframe)