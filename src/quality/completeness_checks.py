from __future__ import annotations

import pandas as pd

from src.quality.dq_models import (
    DQIssue,
    DQSeverity,
)


def is_evaluated_row(
    df: pd.DataFrame,
) -> pd.Series:
    """
    Détermine si une ligne semble avoir été évaluée.

    Une ligne est considérée comme évaluée si au moins
    un résultat d'audit est renseigné :
    - score_maturite
    - niveau_maturite
    - constat_auditeur
    - categorie_finding

    Cette fonction sert au contrôle Data Quality.
    """

    result_columns = [
        "score_maturite",
        "niveau_maturite",
        "constat_auditeur",
        "categorie_finding",
    ]

    available_columns = [
        column
        for column in result_columns
        if column in df.columns
    ]

    if not available_columns:
        return pd.Series(
            False,
            index=df.index,
        )

    return df[
        available_columns
    ].notna().any(axis=1)


def check_finding_required_after_evaluation(
    df: pd.DataFrame,
) -> list[DQIssue]:
    """
    Vérifie qu'une ligne évaluée possède
    obligatoirement une categorie_finding.
    """

    issues: list[DQIssue] = []

    if "categorie_finding" not in df.columns:
        return issues

    evaluated_mask = is_evaluated_row(df)

    missing_finding_mask = (
        evaluated_mask
        & df["categorie_finding"].isna()
    )

    for _, row in df[
        missing_finding_mask
    ].iterrows():

        issues.append(
            DQIssue(
                rule_id="DQ_COMPLETENESS_001",
                severity=DQSeverity.ERROR,
                message=(
                    "Evaluated row has no "
                    "categorie_finding."
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