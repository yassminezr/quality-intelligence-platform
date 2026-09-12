import pandas as pd

from src.quality.schema_checks import (
    check_required_columns,
)


def test_no_issue_when_required_columns_exist():
    df = pd.DataFrame(
        columns=[
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
        ]
    )

    issues = check_required_columns(df)

    assert issues == []


def test_missing_column_creates_blocking_issue():
    df = pd.DataFrame(
        columns=[
            "source_file",
            "source_sheet",
        ]
    )

    issues = check_required_columns(df)

    assert len(issues) > 0

    assert all(
        issue.severity.value
        == "BLOCKING"
        for issue in issues
    )