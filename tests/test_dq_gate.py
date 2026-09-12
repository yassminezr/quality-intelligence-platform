from src.quality.dq_gate import (
    evaluate_dq_gate,
)
from src.quality.dq_models import (
    DQIssue,
    DQReport,
    DQSeverity,
)


def test_gate_allows_clean_report():
    report = DQReport(
        issues=[]
    )

    result = evaluate_dq_gate(
        report
    )

    assert result.can_continue is True


def test_gate_allows_errors():
    report = DQReport(
        issues=[
            DQIssue(
                rule_id="TEST_ERROR",
                severity=DQSeverity.ERROR,
                message="Business issue",
            )
        ]
    )

    result = evaluate_dq_gate(
        report
    )

    assert result.can_continue is True


def test_gate_blocks_blocking_issue():
    report = DQReport(
        issues=[
            DQIssue(
                rule_id="TEST_BLOCKING",
                severity=DQSeverity.BLOCKING,
                message="Structural issue",
            )
        ]
    )

    result = evaluate_dq_gate(
        report
    )

    assert result.can_continue is False