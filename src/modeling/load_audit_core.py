from __future__ import annotations

import argparse

import pandas as pd

from src.common.database import (
    get_postgres_connection,
)


ACCOUNT_SCOPES = {
    "Compte",
    "Entité et Compte",
}


def is_filled(series: pd.Series) -> pd.Series:
    """
    Considère une valeur comme renseignée
    si elle n'est ni NULL ni vide.
    """

    return (
        series.notna()
        & series.astype(str).str.strip().ne("")
    )


def calculate_completion_rate(
    dataframe: pd.DataFrame,
) -> float:
    """
    Calcule le taux de complétude d'un audit.

    Seules les lignes applicables au compte
    sont prises en compte.
    """

    df = dataframe.copy()

    applicable = df[
        df["categorie_scope"].isin(
            ACCOUNT_SCOPES
        )
    ].copy()

    total_controls = len(applicable)

    if total_controls == 0:
        return 0.0

    evaluation_columns = [
        "score_maturite",
        "niveau_maturite",
        "constat_auditeur",
        "categorie_finding",
    ]

    evaluated = pd.Series(
        False,
        index=applicable.index,
    )

    for column in evaluation_columns:
        if column in applicable.columns:
            evaluated = (
                evaluated
                | is_filled(
                    applicable[column]
                )
            )

    evaluated_count = int(
        evaluated.sum()
    )

    return round(
        (
            evaluated_count
            / total_controls
        )
        * 100,
        2,
    )


def propose_audit_status(
    completion_rate: float,
) -> str:
    """
    Applique la règle métier de proposition
    du statut d'audit.
    """

    if completion_rate == 0:
        return "non_audite"

    if completion_rate < 65:
        return "en_cours"

    if completion_rate == 65:
        return "a_valider"

    return "audite"


def load_audit_core(
    batch_id: str,
) -> dict[str, int]:
    """
    Alimente :
    - core.account
    - core.campaign
    - core.audit

    à partir d'un batch staging.
    """

    connection = get_postgres_connection()

    try:
        # ---------------------------------
        # 1. Charger le staging du batch
        # ---------------------------------

        dataframe = pd.read_sql_query(
            """
            SELECT *
            FROM staging.standardized_audits
            WHERE batch_id = %s;
            """,
            connection,
            params=(batch_id,),
        )

        if dataframe.empty:
            raise ValueError(
                f"No staging data found "
                f"for batch {batch_id}"
            )

        # ---------------------------------
        # 2. Lire la campagne du batch
        # ---------------------------------

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT campaign
                FROM metadata.ingestion_batch
                WHERE batch_id = %s;
                """,
                (batch_id,),
            )

            result = cursor.fetchone()

            if result is None:
                raise ValueError(
                    f"Batch metadata not found: "
                    f"{batch_id}"
                )

            campaign_name = result[0]

            # ---------------------------------
            # 3. Campaign
            # ---------------------------------

            cursor.execute(
                """
                INSERT INTO core.campaign (
                    campaign_name,
                    status
                )
                VALUES (
                    %s,
                    %s
                )
                ON CONFLICT (campaign_name)
                DO UPDATE SET
                    status = EXCLUDED.status
                RETURNING campaign_id;
                """,
                (
                    campaign_name,
                    "active",
                ),
            )

            campaign_id = (
                cursor.fetchone()[0]
            )

            account_count = 0
            audit_count = 0

            # ---------------------------------
            # 4. Accounts + audits
            # ---------------------------------

            account_names = sorted(
                dataframe[
                    "source_sheet"
                ]
                .dropna()
                .unique()
            )

            for account_name in account_names:

                account_df = dataframe[
                    dataframe["source_sheet"]
                    == account_name
                ]

                completion_rate = (
                    calculate_completion_rate(
                        account_df
                    )
                )

                proposed_status = (
                    propose_audit_status(
                        completion_rate
                    )
                )

                # Account
                cursor.execute(
                    """
                    INSERT INTO core.account (
                        account_name
                    )
                    VALUES (%s)
                    ON CONFLICT (account_name)
                    DO UPDATE SET
                        is_active = TRUE
                    RETURNING account_id;
                    """,
                    (account_name,),
                )

                account_id = (
                    cursor.fetchone()[0]
                )

                account_count += 1

                # Audit
                cursor.execute(
                    """
                    INSERT INTO core.audit (
                        account_id,
                        campaign_id,
                        completion_rate,
                        current_proposed_status,
                        current_validated_status,
                        status_last_updated_at
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        NULL,
                        NOW()
                    )
                    ON CONFLICT (
                        account_id,
                        campaign_id
                    )
                    DO UPDATE SET
                        completion_rate =
                            EXCLUDED.completion_rate,

                        current_proposed_status =
                            EXCLUDED.current_proposed_status,

                        status_last_updated_at =
                            NOW(),

                        updated_at =
                            NOW();
                    """,
                    (
                        account_id,
                        campaign_id,
                        completion_rate,
                        proposed_status,
                    ),
                )

                audit_count += 1

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return {
        "accounts": account_count,
        "audits": audit_count,
    }


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Load accounts, campaign and audits "
            "into PostgreSQL core."
        )
    )

    parser.add_argument(
        "--batch-id",
        required=True,
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    result = load_audit_core(
        batch_id=args.batch_id
    )

    print(
        "Core audit loading completed."
    )

    print(
        "Accounts:",
        result["accounts"],
    )

    print(
        "Audits:",
        result["audits"],
    )


if __name__ == "__main__":
    main()