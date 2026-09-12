import pandas as pd

from src.quality.dq_engine import (
    run_data_quality,
)


def create_valid_dataframe():
    return pd.DataFrame(
        {
            "source_file": [
                "test.xlsx"
            ],
            "source_sheet": [
                "RAM"
            ],
            "source_row_number": [
                1
            ],
            "clause_iso": [
                "4.1"
            ],
            "intitule_iso": [
                "Contexte"
            ],
            "libelle_terrain": [
                "Contexte organisation"
            ],
            "controle_attendu": [
                "Vérifier le contexte"
            ],
            "categorie_finding": [
                "NA"
            ],
            "score_maturite": [
                4
            ],
            "niveau_maturite": [
                "Totalement en place/Proactif"
            ],
            "constat_auditeur": [
                "Conforme"
            ],
            "action_corrective": [
                None
            ],
            "responsable_action": [
                None
            ],
            "date_debut": [
                None
            ],
            "date_cloture": [
                None
            ],
            "statut_action": [
                None
            ],
        }
    )


def test_valid_dataset_has_no_issue():
    df = create_valid_dataframe()

    report = run_data_quality(df)

    assert report.total_issues == 0
    assert report.has_blocking_issues is False


def test_invalid_domain_creates_errors():
    df = create_valid_dataframe()

    df.loc[
        0,
        "score_maturite"
    ] = 8

    df.loc[
        0,
        "categorie_finding"
    ] = "Unknown Category"

    report = run_data_quality(df)

    assert report.error_count >= 2

    assert (
        report.has_blocking_issues
        is False
    )


def test_missing_required_column_is_blocking():
    df = create_valid_dataframe()

    df = df.drop(
        columns=[
            "clause_iso"
        ]
    )

    report = run_data_quality(df)

    assert report.blocking_count >= 1

    assert (
        report.has_blocking_issues
        is True
    )