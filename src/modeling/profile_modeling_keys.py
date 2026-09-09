from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Standardized dataset not found: {path}"
        )

    return pd.read_csv(
        path,
        encoding="utf-8-sig",
    )


def profile_candidate_keys(df: pd.DataFrame) -> None:

    print("=== Modeling key profiling ===")

    print(f"\nTotal rows: {len(df)}")

    print(
        "Distinct accounts: "
        f"{df['source_sheet'].nunique()}"
    )

    print(
        "Distinct source row numbers: "
        f"{df['source_row_number'].nunique()}"
    )

    print(
        "Distinct clause_iso: "
        f"{df['clause_iso'].nunique()}"
    )

    print(
        "Distinct libelle_terrain: "
        f"{df['libelle_terrain'].nunique()}"
    )

    print(
        "Distinct controle_attendu: "
        f"{df['controle_attendu'].nunique()}"
    )

    clause_label_count = (
        df[
            [
                "clause_iso",
                "libelle_terrain",
            ]
        ]
        .drop_duplicates()
        .shape[0]
    )

    full_control_count = (
        df[
            [
                "clause_iso",
                "libelle_terrain",
                "controle_attendu",
            ]
        ]
        .drop_duplicates()
        .shape[0]
    )

    print(
        "Distinct clause_iso + libelle_terrain: "
        f"{clause_label_count}"
    )

    print(
        "Distinct clause_iso + libelle_terrain "
        "+ controle_attendu: "
        f"{full_control_count}"
    )


def check_reference_consistency(
    df: pd.DataFrame,
) -> None:
    """
    Vérifie si un même numéro de ligne source
    représente le même contrôle dans tous les comptes.
    """

    reference_columns = [
        "source_row_number",
        "clause_iso",
        "intitule_iso",
        "libelle_terrain",
        "controle_attendu",
        "categorie_scope",
        "reference_edge",
        "preuves_attendues",
    ]

    reference = df[
        reference_columns
    ].drop_duplicates()

    counts = (
        reference
        .groupby("source_row_number")
        .size()
    )

    inconsistent = counts[
        counts > 1
    ]

    print("\n=== Reference consistency ===")

    print(
        "Source row numbers with multiple "
        "reference definitions: "
        f"{len(inconsistent)}"
    )

    if not inconsistent.empty:

        print("\nPotential inconsistencies:")

        for row_number in inconsistent.index:
            print(f"- source_row_number={row_number}")


def check_account_control_uniqueness(
    df: pd.DataFrame,
) -> None:
    """
    Vérifie si une combinaison compte + numéro de contrôle
    apparaît plusieurs fois.
    """

    duplicates = df.duplicated(
        subset=[
            "source_sheet",
            "source_row_number",
        ],
        keep=False,
    )

    duplicate_count = int(
        duplicates.sum()
    )

    print("\n=== Account/control uniqueness ===")

    print(
        "Duplicate account + source_row_number rows: "
        f"{duplicate_count}"
    )


def parse_arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default=Path(
            "data/standardized/"
            "standardized_audits.csv"
        ),
        type=Path,
    )

    return parser.parse_args()


def main():

    args = parse_arguments()

    df = load_data(args.input)

    profile_candidate_keys(df)

    check_reference_consistency(df)

    check_account_control_uniqueness(df)


if __name__ == "__main__":
    main()