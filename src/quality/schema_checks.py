from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.quality.dq_models import (
    DQIssue,
    DQSeverity,
)


REQUIRED_COLUMNS = {
    "source_file",
    "source_sheet",
    "source_row_number",
    "clause_iso",
    "intitule_iso",
    "libelle_terrain",
    "controle_attendu",
    "categorie_finding",
    "score_maturite",
    "action_corrective",
    "responsable_action",
    "date_debut",
    "date_cloture",
    "statut_action",
}


def check_required_columns(
    df: pd.DataFrame,
) -> list[DQIssue]:
    """
    Vérifie que toutes les colonnes obligatoires
    sont présentes dans le dataset standardisé.
    """

    issues: list[DQIssue] = []

    missing_columns = (
        REQUIRED_COLUMNS
        - set(df.columns)
    )

    for column in sorted(missing_columns):
        issues.append(
            DQIssue(
                rule_id="DQ_SCHEMA_001",
                severity=DQSeverity.BLOCKING,
                message=(
                    f"Required column missing: {column}"
                ),
            )
        )

    return issues


def load_standardized_csv(
    path: Path,
) -> pd.DataFrame:
    """
    Charge le fichier standardisé.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Standardized file not found: {path}"
        )

    return pd.read_csv(
        path,
        encoding="utf-8-sig",
    )