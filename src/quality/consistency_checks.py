from __future__ import annotations

import pandas as pd

from src.quality.dq_models import (
    DQIssue,
    DQSeverity,
)


def _is_filled(series: pd.Series) -> pd.Series:
    """
    Retourne True lorsque la valeur est réellement renseignée.
    Gère les NaN et les chaînes vides.
    """

    return (
        series.notna()
        & series.astype(str).str.strip().ne("")
    )


def check_na_without_corrective_action(
    df: pd.DataFrame,
) -> list[DQIssue]:
    """
    Règle :
    categorie_finding = NA
    => aucune action corrective ne doit exister.
    """

    issues: list[DQIssue] = []

    required_columns = {
        "categorie_finding",
        "action_corrective",
    }

    if not required_columns.issubset(df.columns):
        return issues

    finding_values = (
        df["categorie_finding"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    action_present = _is_filled(
        df["action_corrective"]
    )

    invalid_mask = (
        finding_values.eq("NA")
        & action_present
    )

    for _, row in df[invalid_mask].iterrows():

        issues.append(
            DQIssue(
                rule_id="DQ_CONSISTENCY_001",
                severity=DQSeverity.ERROR,
                message=(
                    "categorie_finding is NA "
                    "but a corrective action is present."
                ),
                source_file=row.get(
                    "source_file"
                ),
                source_sheet=row.get(
                    "source_sheet"
                ),
                source_row_number=str(
                    row.get(
                        "source_row_number"
                    )
                ),
            )
        )

    return issues


def check_action_requires_valid_finding(
    df: pd.DataFrame,
) -> list[DQIssue]:
    """
    Règle :
    si une action corrective existe,
    le finding doit être renseigné
    et ne doit pas être NA.
    """

    issues: list[DQIssue] = []

    required_columns = {
        "categorie_finding",
        "action_corrective",
    }

    if not required_columns.issubset(df.columns):
        return issues

    finding_values = (
        df["categorie_finding"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    action_present = _is_filled(
        df["action_corrective"]
    )

    invalid_mask = (
        action_present
        & (
            finding_values.eq("")
            | finding_values.eq("NA")
        )
    )

    for _, row in df[invalid_mask].iterrows():

        issues.append(
            DQIssue(
                rule_id="DQ_CONSISTENCY_002",
                severity=DQSeverity.ERROR,
                message=(
                    "Corrective action exists but "
                    "categorie_finding is missing or NA."
                ),
                source_file=row.get(
                    "source_file"
                ),
                source_sheet=row.get(
                    "source_sheet"
                ),
                source_row_number=str(
                    row.get(
                        "source_row_number"
                    )
                ),
            )
        )

    return issues


def check_closed_action_has_closure_date(
    df: pd.DataFrame,
) -> list[DQIssue]:
    """
    Règle :
    une action clôturée doit avoir une date_cloture.
    """

    issues: list[DQIssue] = []

    required_columns = {
        "statut_action",
        "date_cloture",
    }

    if not required_columns.issubset(df.columns):
        return issues

    status_values = (
        df["statut_action"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    closure_date_present = _is_filled(
        df["date_cloture"]
    )

    invalid_mask = (
        status_values.eq("clôturé")
        & ~closure_date_present
    )

    for _, row in df[invalid_mask].iterrows():

        issues.append(
            DQIssue(
                rule_id="DQ_CONSISTENCY_003",
                severity=DQSeverity.ERROR,
                message=(
                    "Closed corrective action "
                    "has no date_cloture."
                ),
                source_file=row.get(
                    "source_file"
                ),
                source_sheet=row.get(
                    "source_sheet"
                ),
                source_row_number=str(
                    row.get(
                        "source_row_number"
                    )
                ),
            )
        )

    return issues