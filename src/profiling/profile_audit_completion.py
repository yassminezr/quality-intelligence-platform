from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ACCOUNT_SCOPES = {
    "Compte",
    "Entité et Compte",
}


def load_data(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Standardized dataset not found: {csv_path}"
        )

    return pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
    )


def normalize_text(value) -> str:
    if pd.isna(value):
        return ""

    return str(value).strip()


def is_account_scope(value) -> bool:
    return normalize_text(value) in ACCOUNT_SCOPES


def is_evaluated(row: pd.Series) -> bool:
    """
    Un contrôle est considéré comme traité lorsqu'on trouve
    au moins une information indiquant qu'il a été évalué.

    Il s'agit ici d'un indicateur de profiling,
    PAS encore d'une règle métier finale.
    """

    score_present = pd.notna(
        row.get("score_maturite")
    )

    constat_present = bool(
        normalize_text(
            row.get("constat_auditeur")
        )
    )

    finding_present = bool(
        normalize_text(
            row.get("categorie_finding")
        )
    )

    return (
        score_present
        or constat_present
        or finding_present
    )


def profile_account(
    account_name: str,
    group: pd.DataFrame,
) -> dict:

    account_scope_rows = group[
        group["categorie_scope"].apply(
            is_account_scope
        )
    ].copy()

    account_scope_rows["is_evaluated"] = (
        account_scope_rows.apply(
            is_evaluated,
            axis=1,
        )
    )

    expected_controls = len(
        account_scope_rows
    )

    evaluated_controls = int(
        account_scope_rows["is_evaluated"].sum()
    )

    completion_rate = (
        round(
            evaluated_controls
            / expected_controls
            * 100,
            2,
        )
        if expected_controls > 0
        else 0
    )

    return {
        "source_sheet": account_name,
        "total_checklist_rows": int(
            len(group)
        ),
        "account_scope_controls": int(
            expected_controls
        ),
        "evaluated_controls": (
            evaluated_controls
        ),
        "unevaluated_controls": int(
            expected_controls
            - evaluated_controls
        ),
        "completion_rate": completion_rate,
        "score_count": int(
            account_scope_rows[
                "score_maturite"
            ].notna().sum()
        ),
    }


def build_report(df: pd.DataFrame) -> dict:

    accounts = []

    for account_name, group in df.groupby(
        "source_sheet"
    ):
        accounts.append(
            profile_account(
                account_name,
                group,
            )
        )

    return {
        "account_count": len(accounts),
        "accounts": accounts,
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


def print_report(report: dict) -> None:

    print("Audit completion profiling completed.")
    print()

    for account in report["accounts"]:

        print(
            f"{account['source_sheet']}: "
            f"{account['evaluated_controls']}/"
            f"{account['account_scope_controls']} "
            f"evaluated "
            f"({account['completion_rate']}%)"
        )


def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "Profile account audit completion."
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
            "audit_completion_profile.json"
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

    print()
    print(
        f"Report saved to: {args.output}"
    )


if __name__ == "__main__":
    main()