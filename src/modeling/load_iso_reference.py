from __future__ import annotations

import argparse
import re

import pandas as pd

from src.common.database import (
    get_postgres_connection,
)


def normalize_text(
    value,
):
    """
    Nettoie une valeur texte.
    Retourne None si vide / NaN.
    """

    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


def is_valid_iso_clause(
    value,
) -> bool:
    """
    Vérifie qu'une valeur correspond
    réellement à un numéro de clause ISO.

    Exemples valides :
    4.1
    7.1.1
    8.5.6
    10.2

    Exemples exclus :
    Contexte
    Leadership
    Libellé
    Support
    """

    if value is None:
        return False

    value = str(value).strip()

    return bool(
        re.fullmatch(
            r"(?:[4-9]|10)(?:\.\d+)+",
            value,
        )
    )


def load_iso_reference(
    batch_id: str,
) -> dict[str, int]:
    """
    Alimente :
    - core.iso_clause
    - core.iso_control

    à partir du staging.
    """

    connection = get_postgres_connection()

    try:

        dataframe = pd.read_sql_query(
            """
            SELECT
                clause_iso,
                intitule_iso,
                libelle_terrain,
                controle_attendu,
                categorie_scope,
                reference_edge,
                preuves_attendues
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

        # Nettoyage texte
        for column in dataframe.columns:
            dataframe[column] = (
                dataframe[column]
                .apply(normalize_text)
            )

        # Garder uniquement les vraies clauses ISO
        dataframe = dataframe[
            dataframe["clause_iso"]
            .apply(is_valid_iso_clause)
        ].copy()

        # ---------------------------------
        # 1. Clauses ISO
        # ---------------------------------

        clauses_df = (
            dataframe[
                [
                    "clause_iso",
                    "intitule_iso",
                ]
            ]
            .dropna(
                subset=[
                    "clause_iso",
                ]
            )
            .drop_duplicates(
                subset=[
                    "clause_iso",
                ]
            )
        )

        clause_count = 0
        control_count = 0

        with connection.cursor() as cursor:

            clause_ids = {}

            for row in clauses_df.itertuples(
                index=False
            ):
                cursor.execute(
                    """
                    INSERT INTO core.iso_clause (
                        clause_iso,
                        intitule_iso
                    )
                    VALUES (
                        %s,
                        %s
                    )
                    ON CONFLICT (clause_iso)
                    DO UPDATE SET
                        intitule_iso =
                            EXCLUDED.intitule_iso
                    RETURNING clause_id;
                    """,
                    (
                        row.clause_iso,
                        row.intitule_iso,
                    ),
                )

                clause_id = (
                    cursor.fetchone()[0]
                )

                clause_ids[
                    row.clause_iso
                ] = clause_id

                clause_count += 1

            # ---------------------------------
            # 2. Contrôles ISO
            # ---------------------------------

            controls_df = (
                dataframe[
                    [
                        "clause_iso",
                        "libelle_terrain",
                        "controle_attendu",
                        "categorie_scope",
                        "reference_edge",
                        "preuves_attendues",
                    ]
                ]
                .dropna(
                    subset=[
                        "clause_iso",
                        "libelle_terrain",
                    ]
                )
                .drop_duplicates(
                    subset=[
                        "clause_iso",
                        "libelle_terrain",
                    ]
                )
            )

            for row in controls_df.itertuples(
                index=False
            ):

                clause_id = clause_ids.get(
                    row.clause_iso
                )

                if clause_id is None:
                    continue

                cursor.execute(
                    """
                    INSERT INTO core.iso_control (
                        clause_id,
                        libelle_terrain,
                        controle_attendu,
                        categorie_scope,
                        reference_edge,
                        preuves_attendues
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    ON CONFLICT (
                        clause_id,
                        libelle_terrain
                    )
                    DO UPDATE SET
                        controle_attendu =
                            EXCLUDED.controle_attendu,

                        categorie_scope =
                            EXCLUDED.categorie_scope,

                        reference_edge =
                            EXCLUDED.reference_edge,

                        preuves_attendues =
                            EXCLUDED.preuves_attendues;
                    """,
                    (
                        clause_id,
                        row.libelle_terrain,
                        row.controle_attendu,
                        row.categorie_scope,
                        row.reference_edge,
                        row.preuves_attendues,
                    ),
                )

                control_count += 1

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return {
        "clauses": clause_count,
        "controls": control_count,
    }


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Load ISO clauses and controls "
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

    result = load_iso_reference(
        batch_id=args.batch_id
    )

    print(
        "ISO reference loading completed."
    )

    print(
        "Clauses:",
        result["clauses"],
    )

    print(
        "Controls:",
        result["controls"],
    )


if __name__ == "__main__":
    main()