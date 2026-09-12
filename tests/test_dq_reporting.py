from pathlib import Path

from src.quality.dq_gate import (
    evaluate_dq_gate,
)
from src.quality.dq_models import (
    DQIssue,
    DQReport,
    DQSeverity,
)
from src.quality.dq_reporting import (
    save_business_reports,
)


def test_dq_gate_allows_errors():
    report = DQReport(
        issues=[
            DQIssue(
                rule_id="TEST_ERROR",
                severity=DQSeverity.ERROR,
                message="Business error",
            )
        ]
    )

    result = evaluate_dq_gate(report)

    assert result.can_continue is True


def test_dq_gate_blocks_blocking_issue():
    report = DQReport(
        issues=[
            DQIssue(
                rule_id="TEST_BLOCKING",
                severity=DQSeverity.BLOCKING,
                message="Structural error",
            )
        ]
    )

    result = evaluate_dq_gate(report)

    assert result.can_continue is False


def test_business_reports_are_created(
    tmp_path: Path,
):
    report = DQReport(
        issues=[
            DQIssue(
                rule_id="DQ_COMPLETENESS_001",
                severity=DQSeverity.ERROR,
                message=(
                    "Evaluated row has no categorie_finding."
                ),
                source_file="test.xlsx",
                source_sheet="RAM",
                source_row_number="10",
            )
        ]
    )

    save_business_reports(
        report=report,
        output_dir=tmp_path,
    )

    assert (
        tmp_path
        / "dq_issues_business.csv"
    ).exists()

    assert (
        tmp_path
        / "dq_summary_by_rule.csv"
    ).exists()

    assert (
        tmp_path
        / "dq_summary_by_account.csv"
    ).exists()