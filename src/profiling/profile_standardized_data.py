from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


KEY_CATEGORICAL_COLUMNS = [
    "source_sheet",
    "score_maturite",
    "niveau_maturite",
    "categorie_finding",
    "statut_action",
    "indicateur_age",
]


def load_standardized_data(csv_path: Path) -> pd.DataFrame:
    """
    Charge le dataset standardisé produit à l'étape 1.6.
    """

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Standardized dataset not found: {csv_path}"
        )

    return pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
    )


def profile_columns(df: pd.DataFrame) -> list[dict]:
    """
    Produit les statistiques principales de chaque colonne.
    """

    total_rows = len(df)

    column_profiles = []

    for column in df.columns:

        missing_count = int(
            df[column].isna().sum()
        )

        non_null_count = int(
            df[column].notna().sum()
        )

        unique_count = int(
            df[column].nunique(dropna=True)
        )

        missing_percentage = (
            round(
                missing_count / total_rows * 100,
                2,
            )
            if total_rows > 0
            else 0
        )

        column_profiles.append(
            {
                "column": column,
                "non_null_count": non_null_count,
                "missing_count": missing_count,
                "missing_percentage": missing_percentage,
                "unique_count": unique_count,
                "pandas_dtype": str(df[column].dtype),
            }
        )

    return column_profiles


def profile_categorical_values(
    df: pd.DataFrame,
) -> dict:
    """
    Donne la distribution des valeurs des colonnes
    métier importantes.
    """

    distributions = {}

    for column in KEY_CATEGORICAL_COLUMNS:

        if column not in df.columns:
            continue

        counts = (
            df[column]
            .fillna("<MISSING>")
            .astype(str)
            .value_counts(dropna=False)
        )

        distributions[column] = {
            str(value): int(count)
            for value, count in counts.items()
        }

    return distributions


def profile_accounts(df: pd.DataFrame) -> list[dict]:
    """
    Produit quelques statistiques simples par compte/feuille.
    """

    results = []

    for sheet_name, group in df.groupby(
        "source_sheet",
        dropna=False,
    ):

        results.append(
            {
                "source_sheet": str(sheet_name),
                "row_count": int(len(group)),
                "score_filled_count": int(
                    group["score_maturite"]
                    .notna()
                    .sum()
                ),
                "finding_filled_count": int(
                    group["categorie_finding"]
                    .notna()
                    .sum()
                ),
                "constat_filled_count": int(
                    group["constat_auditeur"]
                    .notna()
                    .sum()
                ),
                "action_filled_count": int(
                    group["action_corrective"]
                    .notna()
                    .sum()
                ),
            }
        )

    return results


def build_profile(df: pd.DataFrame) -> dict:
    """
    Construit le rapport global de profiling.
    """

    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "column_profiles": profile_columns(df),
        "categorical_distributions": (
            profile_categorical_values(df)
        ),
        "account_profiles": profile_accounts(df),
    }


def save_report(
    report: dict,
    output_path: Path,
) -> None:

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )


def print_summary(report: dict) -> None:
    """
    Affiche un résumé lisible dans le terminal.
    """

    print("Standardized data profiling completed.")
    print(f"Rows: {report['row_count']}")
    print(f"Columns: {report['column_count']}")

    print("\nAccount overview:")

    for account in report["account_profiles"]:

        print(
            f"- {account['source_sheet']}: "
            f"scores={account['score_filled_count']}, "
            f"findings={account['finding_filled_count']}, "
            f"constats={account['constat_filled_count']}, "
            f"actions={account['action_filled_count']}"
        )


def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "Profile standardized QHC audit data."
        )
    )

    parser.add_argument(
        "--input",
        default=Path(
            "data/standardized/standardized_audits.csv"
        ),
        type=Path,
    )

    parser.add_argument(
        "--output",
        default=Path(
            "data/profiling/"
            "standardized_data_profile.json"
        ),
        type=Path,
    )

    return parser.parse_args()


def main():

    args = parse_arguments()

    df = load_standardized_data(args.input)

    report = build_profile(df)

    save_report(
        report=report,
        output_path=args.output,
    )

    print_summary(report)

    print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()