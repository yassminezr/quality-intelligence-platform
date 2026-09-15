from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.common.database import (
    get_postgres_connection,
)


VALID_AUDIT_STATUSES = {
    "non_audite",
    "en_cours",
    "audite",
}


def normalize_text(value):
    """
    Retourne un texte propre ou None.
    """

    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


def normalize_datetime(value):
    """
    Convertit une date en datetime.

    Une valeur vide ou invalide retourne None.
    """

    value = normalize_text(value)

    if value is None:
        return None

    parsed = pd.to_datetime(
        value,
        errors="coerce",
    )

    if pd.isna(parsed):
        return None

    return parsed.to_pydatetime()


def load_audit_validations(
    csv_path: Path,
    campaign_name: str,
) -> dict[str, int]:

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Validation file not found: "
            f"{csv_path}"
        )

    dataframe = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
    )

    required_columns = {
        "source_sheet",
        "statut_valide",
    }

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    # Colonnes facultatives
    if "date_validation" not in dataframe.columns:
        dataframe["date_validation"] = None

    if "valide_par" not in dataframe.columns:
        dataframe["valide_par"] = None

    connection = get_postgres_connection()

    updated_count = 0
    history_count = 0
    unchanged_count = 0

    try:
        with connection.cursor() as cursor:

            # -----------------------------
            # Campaign
            # -----------------------------

            cursor.execute(
                """
                SELECT campaign_id
                FROM core.campaign
                WHERE campaign_name = %s;
                """,
                (campaign_name,),
            )

            result = cursor.fetchone()

            if result is None:
                raise ValueError(
                    f"Campaign not found: "
                    f"{campaign_name}"
                )

            campaign_id = result[0]

            # -----------------------------
            # Parcourir validations
            # -----------------------------

            for row in dataframe.itertuples(
                index=False
            ):

                account_name = normalize_text(
                    row.source_sheet
                )

                validated_status = normalize_text(
                    row.statut_valide
                )

                validation_date = normalize_datetime(
                    row.date_validation
                )

                validated_by = normalize_text(
                    row.valide_par
                )

                if account_name is None:
                    continue

                if (
                    validated_status
                    not in VALID_AUDIT_STATUSES
                ):
                    raise ValueError(
                        f"Invalid validated status "
                        f"for {account_name}: "
                        f"{validated_status}"
                    )

                # -----------------------------
                # Trouver l'audit
                # -----------------------------

                cursor.execute(
                    """
                    SELECT
                        au.audit_id,
                        au.current_proposed_status,
                        au.current_validated_status

                    FROM core.audit au

                    JOIN core.account acc
                        ON acc.account_id =
                           au.account_id

                    WHERE
                        acc.account_name = %s
                        AND au.campaign_id = %s;
                    """,
                    (
                        account_name,
                        campaign_id,
                    ),
                )

                audit = cursor.fetchone()

                if audit is None:
                    raise ValueError(
                        f"Audit not found for "
                        f"{account_name} / "
                        f"{campaign_name}"
                    )

                audit_id = audit[0]
                proposed_status = audit[1]
                current_validated_status = audit[2]

                # -----------------------------
                # Aucun changement
                # -----------------------------

                if (
                    current_validated_status
                    == validated_status
                ):
                    unchanged_count += 1
                    continue

                # -----------------------------
                # Mise à jour statut officiel
                # -----------------------------

                cursor.execute(
                    """
                    UPDATE core.audit
                    SET
                        current_validated_status = %s,
                        status_last_updated_at = NOW(),
                        updated_at = NOW()
                    WHERE audit_id = %s;
                    """,
                    (
                        validated_status,
                        audit_id,
                    ),
                )

                updated_count += 1

                # -----------------------------
                # Historique validation
                # -----------------------------

                cursor.execute(
                    """
                    INSERT INTO
                        core.audit_status_validation (
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
                        %s,
                        %s
                    );
                    """,
                    (
                        audit_id,
                        proposed_status,
                        validated_status,
                        validation_date,
                        validated_by,
                    ),
                )

                history_count += 1

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return {
        "updated": updated_count,
        "history_created": history_count,
        "unchanged": unchanged_count,
    }


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Load official audit status "
            "validations into PostgreSQL core."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--campaign",
        required=True,
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    result = load_audit_validations(
        csv_path=args.input,
        campaign_name=args.campaign,
    )

    print(
        "Audit validation loading completed."
    )

    print(
        "Updated audits:",
        result["updated"],
    )

    print(
        "History rows created:",
        result["history_created"],
    )

    print(
        "Unchanged audits:",
        result["unchanged"],
    )


if __name__ == "__main__":
    main()