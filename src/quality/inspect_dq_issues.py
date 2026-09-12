from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--issues",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--data",
        required=True,
        type=Path,
    )

    args = parser.parse_args()

    issues = pd.read_csv(
        args.issues,
        encoding="utf-8-sig",
    )

    data = pd.read_csv(
        args.data,
        encoding="utf-8-sig",
    )

    keys = [
        "source_file",
        "source_sheet",
        "source_row_number",
    ]

    # Harmoniser source_row_number pour le merge
    issues["source_row_number"] = (
        issues["source_row_number"]
        .astype(str)
        .str.strip()
    )

    data["source_row_number"] = (
        data["source_row_number"]
        .astype(str)
        .str.strip()
    )

    merged = issues.merge(
        data,
        on=keys,
        how="left",
        suffixes=("_issue", ""),
    )

    columns_to_show = [
        "rule_id",
        "source_sheet",
        "source_row_number",
        "score_maturite",
        "niveau_maturite",
        "constat_auditeur",
        "categorie_finding",
        "action_corrective",
        "responsable_action",
        "statut_action",
    ]

    for rule_id in sorted(
        merged["rule_id"].unique()
    ):
        print(
            f"\n=== {rule_id} ==="
        )

        subset = merged[
            merged["rule_id"] == rule_id
        ]

        print(
            subset[
                columns_to_show
            ]
            .head(20)
            .to_string(index=False)
        )

    # Identifier les lignes ayant plusieurs anomalies
    duplicate_issues = (
        issues
        .groupby(keys)
        .size()
        .reset_index(
            name="issue_count"
        )
    )

    duplicate_issues = duplicate_issues[
        duplicate_issues["issue_count"] > 1
    ]

    print(
        "\n=== ROWS WITH MULTIPLE ISSUES ==="
    )

    print(
        duplicate_issues.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()