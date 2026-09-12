from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to dq_issues.csv",
    )

    args = parser.parse_args()

    df = pd.read_csv(
        args.input,
        encoding="utf-8-sig",
    )

    print("=== DQ ISSUES ANALYSIS ===")

    print("\nTotal issues:")
    print(len(df))

    print("\nIssues by rule:")
    print(
        df["rule_id"]
        .value_counts()
        .sort_index()
    )

    print("\nIssues by severity:")
    print(
        df["severity"]
        .value_counts()
    )

    affected_rows = (
        df[
            [
                "source_file",
                "source_sheet",
                "source_row_number",
            ]
        ]
        .drop_duplicates()
    )

    print(
        "\nUnique affected source rows:",
        len(affected_rows),
    )

    print("\nTop affected sheets:")
    print(
        df["source_sheet"]
        .value_counts()
        .head(10)
    )


if __name__ == "__main__":
    main()