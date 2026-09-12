from __future__ import annotations

from dataclasses import dataclass

from src.quality.dq_models import DQReport


@dataclass
class DQGateResult:
    """
    Résultat de la décision Data Quality.

    can_continue :
        True si le pipeline peut continuer vers PostgreSQL.

    reason :
        Explication lisible de la décision.
    """

    can_continue: bool
    reason: str


def evaluate_dq_gate(
    report: DQReport,
) -> DQGateResult:
    """
    Applique la politique Data Quality du projet.

    Politique actuelle :

    - WARNING :
      le pipeline continue.

    - ERROR :
      le pipeline continue,
      mais les anomalies doivent être visibles
      dans le rapport Data Quality.

    - BLOCKING :
      le pipeline s'arrête.
    """

    if report.has_blocking_issues:
        return DQGateResult(
            can_continue=False,
            reason=(
                "Pipeline blocked because "
                f"{report.blocking_count} BLOCKING "
                "Data Quality issue(s) were detected."
            ),
        )

    if report.error_count > 0:
        return DQGateResult(
            can_continue=True,
            reason=(
                "Pipeline can continue, but "
                f"{report.error_count} Data Quality "
                "ERROR issue(s) were detected. "
                "They must be reviewed by the Quality team."
            ),
        )

    if report.warning_count > 0:
        return DQGateResult(
            can_continue=True,
            reason=(
                "Pipeline can continue with "
                f"{report.warning_count} warning(s)."
            ),
        )

    return DQGateResult(
        can_continue=True,
        reason=(
            "Pipeline can continue. "
            "No Data Quality issue was detected."
        ),
    )