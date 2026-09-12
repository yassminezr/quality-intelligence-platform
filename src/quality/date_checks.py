from __future__ import annotations

from datetime import date

import pandas as pd

from src.quality.dq_models import (
    DQIssue,
    DQSeverity,
)


def parse_date_series(
    series: pd.Series,
) -> pd.Series:
    """
    Convertit une colonne en dates pandas.

    Les valeurs impossibles à parser deviennent NaT.
    """

    return pd.to_datetime(
        series,
        errors="coerce",
    )


def calculate_action_age(
    date_debut,
    date_cloture,
    statut_action,
    today: date | None = None,
) -> int | None:
    """
    Calcule l'âge d'une action corrective.

    - action ouverte / en cours :
      today - date_debut

    - action clôturée :
      date_cloture - date_debut

    Retourne None si le calcul est impossible.
    """

    if today is None:
        today = date.today()

    start = pd.to_datetime(
        date_debut,
        errors="coerce",
    )

    if pd.isna(start):
        return None

    status = (
        ""
        if pd.isna(statut_action)
        else str(statut_action).strip().lower()
    )

    if status == "clôturé":
        end = pd.to_datetime(
            date_cloture,
            errors="coerce",
        )

        if pd.isna(end):
            return None

        return (
            end.date()
            - start.date()
        ).days

    return (
        today
        - start.date()
    ).days


def calculate_age_indicator(
    age_days: int | None,
) -> str | None:
    """
    Convertit age_jours en indicateur métier.
    """

    if age_days is None:
        return None

    if age_days < 0:
        return None

    if age_days <= 30:
        return "Normal"

    if age_days <= 60:
        return "Alerte"

    if age_days <= 90:
        return "Critique"

    return "Escalade management"


def check_invalid_dates(
    df: pd.DataFrame,
) -> list[DQIssue]:
    """
    Détecte les dates renseignées mais impossibles à parser.
    """

    issues: list[DQIssue] = []

    for column in [
        "date_debut",
        "date_cloture",
    ]:

        if column not in df.columns:
            continue

        parsed = parse_date_series(
            df[column]
        )

        invalid_mask = (
            df[column].notna()
            & parsed.isna()
        )

        for _, row in df[
            invalid_mask
        ].iterrows():

            issues.append(
                DQIssue(
                    rule_id="DQ_DATE_001",
                    severity=DQSeverity.ERROR,
                    message=(
                        f"Invalid date value in {column}: "
                        f"{row.get(column)}"
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


def check_closure_before_start(
    df: pd.DataFrame,
) -> list[DQIssue]:
    """
    Vérifie que date_cloture n'est pas
    antérieure à date_debut.
    """

    issues: list[DQIssue] = []

    required_columns = {
        "date_debut",
        "date_cloture",
    }

    if not required_columns.issubset(
        df.columns
    ):
        return issues

    start = parse_date_series(
        df["date_debut"]
    )

    end = parse_date_series(
        df["date_cloture"]
    )

    invalid_mask = (
        start.notna()
        & end.notna()
        & (end < start)
    )

    for _, row in df[
        invalid_mask
    ].iterrows():

        issues.append(
            DQIssue(
                rule_id="DQ_DATE_002",
                severity=DQSeverity.ERROR,
                message=(
                    "date_cloture is before "
                    "date_debut."
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