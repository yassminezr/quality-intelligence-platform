from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


COLUMNS_TO_PROFILE = [
    "score_maturite",
    "niveau_maturite",
    "categorie_finding",
    "statut_action",
    "indicateur_age",
    "categorie_scope",
]


EXPECTED_SCORE_MIN = 1
EXPECTED_SCORE_MAX = 5


def load_data(csv_path: Path) -> pd.DataFrame:
    """
    Charge les données standardisées.
    """

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Standardized dataset not found: {csv_path}"
        )

    return pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
    )


def normalize_text(value) -> str:
    """
    Normalisation légère uniquement pour le profiling.

    On ne modifie pas les données sources.
    """

    if pd.isna(value):
        return ""

    return str(value).strip()


def profile_value_distribution(
    series: pd.Series,
) -> dict:
    """
    Calcule la distribution des valeurs d'une colonne.
    """

    cleaned = (
        series
        .dropna()
        .astype(str)
        .str.strip()
    )

    counts = cleaned.value_counts()

    return {
        "non_null_count": int(series.notna().sum()),
        "missing_count": int(series.isna().sum()),
        "unique_count": int(cleaned.nunique()),
        "values": {
            str(value): int(count)
            for value, count in counts.items()
        },
    }


def profile_scores(
    df: pd.DataFrame,
) -> dict:
    """
    Analyse spécifiquement score_maturite.
    """

    numeric_scores = pd.to_numeric(
        df["score_maturite"],
        errors="coerce",
    )

    invalid_numeric_values = df[
        df["score_maturite"].notna()
        & numeric_scores.isna()
    ]["score_maturite"].tolist()

    out_of_range = numeric_scores[
        numeric_scores.notna()
        & (
            (numeric_scores < EXPECTED_SCORE_MIN)
            | (numeric_scores > EXPECTED_SCORE_MAX)
        )
    ]

    return {
        "distribution": profile_value_distribution(
            df["score_maturite"]
        ),
        "invalid_numeric_values": [
            str(value)
            for value in invalid_numeric_values
        ],
        "out_of_range_values": [
            float(value)
            for value in out_of_range.tolist()
        ],
        "out_of_range_count": int(
            len(out_of_range)
        ),
    }


def detect_text_variants(
    series: pd.Series,
) -> dict:
    """
    Cherche des variantes potentielles dues aux espaces
    ou à la casse.

    Exemple :
    'Clôturé'
    'clôturé'
    'Clôturé '
    """

    original_values = (
        series
        .dropna()
        .astype(str)
    )

    groups = {}

    for original in original_values.unique():

        normalized = (
            original
            .strip()
            .lower()
        )

        groups.setdefault(
            normalized,
            [],
        ).append(original)

    variants = {
        normalized: values
        for normalized, values in groups.items()
        if len(set(values)) > 1
    }

    return variants


def profile_text_column(
    df: pd.DataFrame,
    column: str,
) -> dict:

    return {
        "distribution": profile_value_distribution(
            df[column]
        ),
        "potential_format_variants": (
            detect_text_variants(
                df[column]
            )
        ),
    }


def build_report(
    df: pd.DataFrame,
) -> dict:

    report = {
        "row_count": int(len(df)),
        "columns": {},
    }

    for column in COLUMNS_TO_PROFILE:

        if column not in df.columns:
            report["columns"][column] = {
                "error": "column_not_found"
            }
            continue

        if column == "score_maturite":
            report["columns"][column] = (
                profile_scores(df)
            )
        else:
            report["columns"][column] = (
                profile_text_column(
                    df,
                    column,
                )
            )

    return report


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


def print_report(
    report: dict,
) -> None:

    print(
        "Business value profiling completed."
    )

    for column, profile in report[
        "columns"
    ].items():

        print(f"\n=== {column} ===")

        if "error" in profile:
            print(profile["error"])
            continue

        distribution = profile[
            "distribution"
        ]

        print(
            f"Non-null: "
            f"{distribution['non_null_count']}"
        )

        print(
            f"Missing: "
            f"{distribution['missing_count']}"
        )

        print(
            f"Unique values: "
            f"{distribution['unique_count']}"
        )

        print("Values:")

        for value, count in distribution[
            "values"
        ].items():

            print(
                f"  - {value}: {count}"
            )

        if column == "score_maturite":

            print(
                "Out-of-range scores: "
                f"{profile['out_of_range_count']}"
            )

        else:

            variants = profile[
                "potential_format_variants"
            ]

            if variants:
                print(
                    "Potential formatting variants:"
                )

                for normalized, values in (
                    variants.items()
                ):
                    print(
                        f"  - {normalized}: "
                        f"{values}"
                    )


def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "Profile business values "
            "from standardized QHC data."
        )
    )

    parser.add_argument(
        "--input",
        default=Path(
            "data/standardized/"
            "standardized_audits.csv"
        ),
        type=Path,
    )

    parser.add_argument(
        "--output",
        default=Path(
            "data/profiling/"
            "business_value_profile.json"
        ),
        type=Path,
    )

    return parser.parse_args()


def main():

    args = parse_arguments()

    df = load_data(args.input)

    report = build_report(df)

    save_report(
        report,
        args.output,
    )

    print_report(report)

    print(
        f"\nReport saved to: "
        f"{args.output}"
    )


if __name__ == "__main__":
    main()