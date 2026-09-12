import pandas as pd

from src.quality.completeness_checks import (
    check_finding_required_after_evaluation,
)


def test_unevaluated_row_can_have_no_finding():
    df = pd.DataFrame(
        {
            "score_maturite": [None],
            "niveau_maturite": [None],
            "constat_auditeur": [None],
            "categorie_finding": [None],
        }
    )

    issues = (
        check_finding_required_after_evaluation(
            df
        )
    )

    assert issues == []


def test_evaluated_row_requires_finding():
    df = pd.DataFrame(
        {
            "score_maturite": [3],
            "niveau_maturite": [
                "Largement en place/Stable"
            ],
            "constat_auditeur": [
                "Test constat"
            ],
            "categorie_finding": [None],
            "source_file": [
                "test.xlsx"
            ],
            "source_sheet": [
                "RAM"
            ],
            "source_row_number": [
                12
            ],
        }
    )

    issues = (
        check_finding_required_after_evaluation(
            df
        )
    )

    assert len(issues) == 1

    assert (
        issues[0].rule_id
        == "DQ_COMPLETENESS_001"
    )


def test_evaluated_row_with_na_is_valid():
    df = pd.DataFrame(
        {
            "score_maturite": [4],
            "niveau_maturite": [
                "Totalement en place/Proactif"
            ],
            "constat_auditeur": [
                "Conforme"
            ],
            "categorie_finding": [
                "NA"
            ],
        }
    )

    issues = (
        check_finding_required_after_evaluation(
            df
        )
    )

    assert issues == []