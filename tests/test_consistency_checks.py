import pandas as pd

from src.quality.consistency_checks import (
    check_na_without_corrective_action,
    check_action_requires_valid_finding,
    check_closed_action_has_closure_date,
)


def test_na_with_no_action_is_valid():
    df = pd.DataFrame(
        {
            "categorie_finding": ["NA"],
            "action_corrective": [None],
        }
    )

    issues = (
        check_na_without_corrective_action(
            df
        )
    )

    assert issues == []


def test_na_with_action_creates_issue():
    df = pd.DataFrame(
        {
            "categorie_finding": ["NA"],
            "action_corrective": [
                "Créer une procédure"
            ],
        }
    )

    issues = (
        check_na_without_corrective_action(
            df
        )
    )

    assert len(issues) == 1

    assert (
        issues[0].rule_id
        == "DQ_CONSISTENCY_001"
    )


def test_action_with_valid_finding_is_valid():
    df = pd.DataFrame(
        {
            "categorie_finding": [
                "NC Mineure"
            ],
            "action_corrective": [
                "Mettre à jour la procédure"
            ],
        }
    )

    issues = (
        check_action_requires_valid_finding(
            df
        )
    )

    assert issues == []


def test_action_without_finding_creates_issue():
    df = pd.DataFrame(
        {
            "categorie_finding": [None],
            "action_corrective": [
                "Mettre à jour la procédure"
            ],
        }
    )

    issues = (
        check_action_requires_valid_finding(
            df
        )
    )

    assert len(issues) == 1

    assert (
        issues[0].rule_id
        == "DQ_CONSISTENCY_002"
    )


def test_closed_action_with_date_is_valid():
    df = pd.DataFrame(
        {
            "statut_action": [
                "Clôturé"
            ],
            "date_cloture": [
                "2026-09-15"
            ],
        }
    )

    issues = (
        check_closed_action_has_closure_date(
            df
        )
    )

    assert issues == []


def test_closed_action_without_date_creates_issue():
    df = pd.DataFrame(
        {
            "statut_action": [
                "Clôturé"
            ],
            "date_cloture": [
                None
            ],
        }
    )

    issues = (
        check_closed_action_has_closure_date(
            df
        )
    )

    assert len(issues) == 1

    assert (
        issues[0].rule_id
        == "DQ_CONSISTENCY_003"
    )