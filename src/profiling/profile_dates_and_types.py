from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


DATE_COLUMNS = [
    "date_debut",
    "date_cloture",
]

NUMERIC_COLUMNS = [
    "age_jours",
    "score_maturite",
]


def load_data(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Standardized dataset not found: {csv_path}"
        )

    return pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
    )


def profile_date_column(
    df: pd.DataFrame,
    column: str,
) -> dict:
    """
    Analyse une colonne censée contenir des dates.
    """

    original = df[column]

    parsed = pd.to_datetime(
        original,
        errors="coerce",
    )

    invalid_mask = (
        original.notna()
        & parsed.isna()
    )

    invalid_values = (
        original[invalid_mask]
        .astype(str)
        .value_counts()
    )

    valid_dates = parsed.dropna()

    return {
        "non_null_count": int(
            original.notna().sum()
        ),
        "missing_count": int(
            original.isna().sum()
        ),
        "valid_date_count": int(
            parsed.notna().sum()
        ),
        "invalid_date_count": int(
            invalid_mask.sum()
        ),
        "invalid_values": {
            str(value): int(count)
            for value, count
            in invalid_values.items()
        },
        "min_date": (
            str(valid_dates.min().date())
            if not valid_dates.empty
            else None
        ),
        "max_date": (
            str(valid_dates.max().date())
            if not valid_dates.empty
            else None
        ),
    }


def profile_numeric_column(
    df: pd.DataFrame,
    column: str,
) -> dict:
    """
    Analyse une colonne censée être numérique.
    """

    original = df[column]

    numeric = pd.to_numeric(
        original,
        errors="coerce",
    )

    invalid_mask = (
        original.notna()
        & numeric.isna()
    )

    invalid_values = (
        original[invalid_mask]
        .astype(str)
        .value_counts()
    )

    valid_numeric = numeric.dropna()

    return {
        "non_null_count": int(
            original.notna().sum()
        ),
        "missing_count": int(
            original.isna().sum()
        ),
        "valid_numeric_count": int(
            numeric.notna().sum()
        ),
        "invalid_numeric_count": int(
            invalid_mask.sum()
        ),
        "invalid_values": {
            str(value): int(count)
            for value, count
            in invalid_values.items()
        },
        "negative_count": int(
            (numeric < 0).sum()
        ),
        "min_value": (
            float(valid_numeric.min())
            if not valid_numeric.empty
            else None
        ),
        "max_value": (
            float(valid_numeric.max())
            if not valid_numeric.empty
            else None
        ),
    }


def profile_date_consistency(
    df: pd.DataFrame,
) -> dict:
    """
    Vérifie la cohérence entre date_debut et date_cloture.
    """

    date_debut = pd.to_datetime(
        df["date_debut"],
        errors="coerce",
    )

    date_cloture = pd.to_datetime(
        df["date_cloture"],
        errors="coerce",
    )

    both_present = (
        date_debut.notna()
        & date_cloture.notna()
    )

    closure_before_start = (
        both_present
        & (date_cloture < date_debut)
    )

    same_day = (
        both_present
        & (date_cloture == date_debut)
    )

    return {
        "rows_with_both_dates": int(
            both_present.sum()
        ),
        "closure_before_start_count": int(
            closure_before_start.sum()
        ),
        "same_day_count": int(
            same_day.sum()
        ),
    }


def profile_age_consistency(
    df: pd.DataFrame,
) -> dict:
    """
    Compare age_jours avec la différence entre
    date_cloture et date_debut lorsque les deux existent.

    Attention :
    il s'agit seulement d'un contrôle exploratoire.
    """

    date_debut = pd.to_datetime(
        df["date_debut"],
        errors="coerce",
    )

    date_cloture = pd.to_datetime(
        df["date_cloture"],
        errors="coerce",
    )

    age_jours = pd.to_numeric(
        df["age_jours"],
        errors="coerce",
    )

    comparable_mask = (
        date_debut.notna()
        & date_cloture.notna()
        & age_jours.notna()
    )

    expected_age = (
        date_cloture
        - date_debut
    ).dt.days

    mismatch_mask = (
        comparable_mask
        & (expected_age != age_jours)
    )

    return {
        "comparable_rows": int(
            comparable_mask.sum()
        ),
        "age_mismatch_count": int(
            mismatch_mask.sum()
        ),
    }


def build_report(
    df: pd.DataFrame,
) -> dict:

    return {
        "date_columns": {
            column: profile_date_column(
                df,
                column,
            )
            for column in DATE_COLUMNS
        },
        "numeric_columns": {
            column: profile_numeric_column(
                df,
                column,
            )
            for column in NUMERIC_COLUMNS
        },
        "date_consistency": (
            profile_date_consistency(df)
        ),
        "age_consistency": (
            profile_age_consistency(df)
        ),
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


def print_report(
    report: dict,
) -> None:

    print(
        "Date and type profiling completed."
    )

    for column, profile in (
        report["date_columns"].items()
    ):
        print(f"\n=== {column} ===")
        print(
            f"Non-null: "
            f"{profile['non_null_count']}"
        )
        print(
            f"Missing: "
            f"{profile['missing_count']}"
        )
        print(
            f"Invalid dates: "
            f"{profile['invalid_date_count']}"
        )
        print(
            f"Min date: "
            f"{profile['min_date']}"
        )
        print(
            f"Max date: "
            f"{profile['max_date']}"
        )

    for column, profile in (
        report["numeric_columns"].items()
    ):
        print(f"\n=== {column} ===")
        print(
            f"Non-null: "
            f"{profile['non_null_count']}"
        )
        print(
            f"Invalid numeric: "
            f"{profile['invalid_numeric_count']}"
        )
        print(
            f"Negative values: "
            f"{profile['negative_count']}"
        )
        print(
            f"Min value: "
            f"{profile['min_value']}"
        )
        print(
            f"Max value: "
            f"{profile['max_value']}"
        )

    print("\n=== date_consistency ===")
    print(
        report["date_consistency"]
    )

    print("\n=== age_consistency ===")
    print(
        report["age_consistency"]
    )


def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "Profile dates and numeric types "
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
            "dates_and_types_profile.json"
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