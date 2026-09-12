from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from src.quality.dq_engine import (
    run_data_quality,
)
from src.quality.dq_gate import (
    evaluate_dq_gate,
)
from src.quality.schema_checks import (
    load_standardized_csv,
)
from src.quality.dq_reporting import (
    save_business_reports,
)


def save_dq_report(
    report,
    gate_result,
    output_path: Path,
) -> None:
    """
    Sauvegarde le résumé Data Quality
    et la décision du DQ Gate au format JSON.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = {
        "total_issues": report.total_issues,
        "warning_count": report.warning_count,
        "error_count": report.error_count,
        "blocking_count": report.blocking_count,
        "has_blocking_issues": (
            report.has_blocking_issues
        ),
        "dq_gate": {
            "can_continue": (
                gate_result.can_continue
            ),
            "decision": (
                "CONTINUE"
                if gate_result.can_continue
                else "BLOCK"
            ),
            "reason": gate_result.reason,
        },
    }

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def save_dq_issues(
    report,
    output_path: Path,
) -> None:
    """
    Sauvegarde le détail des anomalies
    au format CSV.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "rule_id",
        "severity",
        "message",
        "source_file",
        "source_sheet",
        "source_row_number",
    ]

    with output_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for issue in report.issues:
            writer.writerow(
                {
                    "rule_id": issue.rule_id,
                    "severity": (
                        issue.severity.value
                    ),
                    "message": issue.message,
                    "source_file": (
                        issue.source_file
                    ),
                    "source_sheet": (
                        issue.source_sheet
                    ),
                    "source_row_number": (
                        issue.source_row_number
                    ),
                }
            )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Run Data Quality checks "
            "on standardized QHC data."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help=(
            "Path to standardized_audits.csv"
        ),
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help=(
            "Directory where DQ outputs "
            "will be written."
        ),
    )

    return parser.parse_args()


def execute_data_quality(
    input_file: Path,
    output_dir: Path,
):
    """
    Exécute le moteur Data Quality et génère
    tous les rapports associés.
    """

    df = load_standardized_csv(
        input_file
    )

    report = run_data_quality(
        df
    )

    gate_result = evaluate_dq_gate(
        report
    )

    report_file = (
        output_dir
        / "dq_report.json"
    )

    issues_file = (
        output_dir
        / "dq_issues.csv"
    )

    save_dq_report(
        report=report,
        gate_result=gate_result,
        output_path=report_file,
    )

    save_dq_issues(
        report=report,
        output_path=issues_file,
    )

    save_business_reports(
        report=report,
        output_dir=output_dir,
    )

    return report, gate_result


def main():
    args = parse_arguments()

    # 1. Exécuter le pipeline Data Quality
    report, gate_result = execute_data_quality(
        input_file=args.input,
        output_dir=args.output_dir,
    )

    # 2. Préparer les chemins des fichiers générés
    report_file = (
        args.output_dir
        / "dq_report.json"
    )

    issues_file = (
        args.output_dir
        / "dq_issues.csv"
    )

    # 3. Afficher le résumé
    print(
        "=== DATA QUALITY REPORT ==="
    )

    print(
        "Total issues:",
        report.total_issues,
    )

    print(
        "Warnings:",
        report.warning_count,
    )

    print(
        "Errors:",
        report.error_count,
    )

    print(
        "Blocking:",
        report.blocking_count,
    )

    print(
        "Has blocking issues:",
        report.has_blocking_issues,
    )

    # 4. Afficher la décision du Gate
    print(
        "\n=== DATA QUALITY GATE ==="
    )

    print(
        "Decision:",
        (
            "CONTINUE"
            if gate_result.can_continue
            else "BLOCK"
        ),
    )

    print(
        "Reason:",
        gate_result.reason,
    )

    # 5. Afficher les fichiers créés
    print(
        "\nFiles created:"
    )

    print(
        report_file
    )

    print(
        issues_file
    )

    print(
        args.output_dir
        / "dq_issues_business.csv"
    )

    print(
        args.output_dir
        / "dq_summary_by_rule.csv"
    )

    print(
        args.output_dir
        / "dq_summary_by_account.csv"
    )


if __name__ == "__main__":
    main()