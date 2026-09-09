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


def check_clause_title_consistency(
    df: pd.DataFrame,
) -> None:
    """
    Vérifie si une même clause ISO possède
    plusieurs intitulés ISO différents.
    """

    relevant = df[
        ["clause_iso", "intitule_iso"]
    ].dropna(
        subset=["clause_iso"]
    ).copy()

    relevant["clause_iso"] = (
        relevant["clause_iso"]
        .astype(str)
        .str.strip()
    )

    relevant["intitule_iso"] = (
        relevant["intitule_iso"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    title_counts = (
        relevant
        .groupby("clause_iso")["intitule_iso"]
        .nunique()
    )

    inconsistent_clauses = title_counts[
        title_counts > 1
    ]

    print("=== ISO clause/title consistency ===")
    print(
        f"Distinct ISO clauses: "
        f"{relevant['clause_iso'].nunique()}"
    )

    print(
        "Clauses with multiple ISO titles: "
        f"{len(inconsistent_clauses)}"
    )

    if inconsistent_clauses.empty:
        print(
            "\nEach clause_iso has a single "
            "intitule_iso in the current dataset."
        )
        return

    print("\nPotential inconsistencies:")

    for clause in inconsistent_clauses.index:
        titles = (
            relevant[
                relevant["clause_iso"] == clause
            ]["intitule_iso"]
            .drop_duplicates()
            .tolist()
        )

        print(f"\n- Clause {clause}")

        for title in titles:
            print(f"  • {title}")


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

    check_clause_title_consistency(df)


if __name__ == "__main__":
    main()