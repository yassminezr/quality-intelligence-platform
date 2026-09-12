from __future__ import annotations

import pandas as pd

from src.quality.dq_models import (
    DQIssue,
    DQSeverity,
)


ALLOWED_FINDING_CATEGORIES = {
    "NC Mineure",
    "NC Majeure",
    "Bonne Pratique",
    "OFI",
    "Observation",
    "NA",
}


def check_score_domain(
    df: pd.DataFrame,
) -> list[DQIssue]:
    """
    Vérifie que les scores renseignés
    sont compris entre 1 et 5.
    """

    issues: list[DQIssue] = []

    if "score_maturite" not in df.columns:
        return issues

    scores = pd.to_numeric(
        df["score_maturite"],
        errors="coerce",
    )

    invalid_mask = (
        df["score_maturite"].notna()
        & (
            scores.isna()
            | (scores < 1)
            | (scores > 5)
        )
    )

    for _, row in df[invalid_mask].iterrows():
        issues.append(
            DQIssue(
                rule_id="DQ_DOMAIN_001",
                severity=DQSeverity.ERROR,
                message=(
                    "Invalid score_maturite. "
                    "Expected a value between 1 and 5."
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


def check_finding_category_domain(
    df: pd.DataFrame,
) -> list[DQIssue]:
    """
    Vérifie que les catégories de finding
    renseignées appartiennent au vocabulaire
    métier officiel.
    """

    issues: list[DQIssue] = []

    if "categorie_finding" not in df.columns:
        return issues

    values = (
        df["categorie_finding"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    invalid_mask = (
        ~values.isin(
            ALLOWED_FINDING_CATEGORIES
        )
    )

    invalid_indexes = (
        values[invalid_mask].index
    )

    for index in invalid_indexes:
        row = df.loc[index]

        issues.append(
            DQIssue(
                rule_id="DQ_DOMAIN_002",
                severity=DQSeverity.ERROR,
                message=(
                    "Invalid categorie_finding: "
                    f"{row.get('categorie_finding')}"
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