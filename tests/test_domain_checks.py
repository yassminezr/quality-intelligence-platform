import pandas as pd

from src.quality.domain_checks import (
    check_finding_category_domain,
    check_score_domain,
)


def test_valid_scores_create_no_issue():
    df = pd.DataFrame(
        {
            "score_maturite": [
                1,
                2,
                3,
                4,
                5,
                None,
            ]
        }
    )

    issues = check_score_domain(df)

    assert issues == []


def test_invalid_score_creates_issue():
    df = pd.DataFrame(
        {
            "score_maturite": [
                8,
            ],
            "source_file": [
                "test.xlsx",
            ],
            "source_sheet": [
                "RAM",
            ],
            "source_row_number": [
                10,
            ],
        }
    )

    issues = check_score_domain(df)

    assert len(issues) == 1

    assert (
        issues[0].rule_id
        == "DQ_DOMAIN_001"
    )


def test_valid_finding_categories_create_no_issue():
    df = pd.DataFrame(
        {
            "categorie_finding": [
                "NC Mineure",
                "NC Majeure",
                "Bonne Pratique",
                "OFI",
                "Observation",
                "NA",
                None,
            ]
        }
    )

    issues = (
        check_finding_category_domain(
            df
        )
    )

    assert issues == []


def test_observation_is_valid_finding_category():
    df = pd.DataFrame(
        {
            "categorie_finding": [
                "Observation",
            ]
        }
    )

    issues = (
        check_finding_category_domain(
            df
        )
    )

    assert issues == []


def test_invalid_finding_category_creates_issue():
    df = pd.DataFrame(
        {
            "categorie_finding": [
                "Unknown Category",
            ],
            "source_file": [
                "test.xlsx",
            ],
            "source_sheet": [
                "RAM",
            ],
            "source_row_number": [
                11,
            ],
        }
    )

    issues = (
        check_finding_category_domain(
            df
        )
    )

    assert len(issues) == 1

    assert (
        issues[0].rule_id
        == "DQ_DOMAIN_002"
    )