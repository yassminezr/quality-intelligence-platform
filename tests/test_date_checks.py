from datetime import date

import pandas as pd

from src.quality.date_checks import (
    calculate_action_age,
    calculate_age_indicator,
    check_invalid_dates,
    check_closure_before_start,
)


def test_open_action_age():
    age = calculate_action_age(
        date_debut="2026-09-01",
        date_cloture=None,
        statut_action="Ouvert",
        today=date(2026, 9, 11),
    )

    assert age == 10


def test_closed_action_age():
    age = calculate_action_age(
        date_debut="2026-09-01",
        date_cloture="2026-09-08",
        statut_action="Clôturé",
        today=date(2026, 9, 20),
    )

    assert age == 7


def test_age_indicator():
    assert (
        calculate_age_indicator(10)
        == "Normal"
    )

    assert (
        calculate_age_indicator(45)
        == "Alerte"
    )

    assert (
        calculate_age_indicator(75)
        == "Critique"
    )

    assert (
        calculate_age_indicator(120)
        == "Escalade management"
    )


def test_invalid_date_creates_issue():
    df = pd.DataFrame(
        {
            "date_debut": [
                "not-a-date"
            ],
            "date_cloture": [
                None
            ],
        }
    )

    issues = check_invalid_dates(df)

    assert len(issues) == 1

    assert (
        issues[0].rule_id
        == "DQ_DATE_001"
    )


def test_closure_before_start_creates_issue():
    df = pd.DataFrame(
        {
            "date_debut": [
                "2026-09-10"
            ],
            "date_cloture": [
                "2026-09-01"
            ],
        }
    )

    issues = (
        check_closure_before_start(
            df
        )
    )

    assert len(issues) == 1

    assert (
        issues[0].rule_id
        == "DQ_DATE_002"
    )