from datetime import date

from src.monitoring.models import ActionMonitoringInput
from src.monitoring.rules import calculate_action_age
import pytest

from src.monitoring.models import EscalationLevel
from src.monitoring.rules import classify_escalation_level


def test_open_action_age_is_calculated_from_current_date():
    action = ActionMonitoringInput(
        action_id="A001",
        date_debut=date(2026, 8, 1),
        is_closed=False,
    )

    age = calculate_action_age(
        action=action,
        current_date=date(2026, 9, 20),
    )

    assert age == 50


def test_missing_start_date_returns_none():
    action = ActionMonitoringInput(
        action_id="A002",
        date_debut=None,
        is_closed=False,
    )

    age = calculate_action_age(
        action=action,
        current_date=date(2026, 9, 20),
    )

    assert age is None


def test_closed_action_keeps_frozen_age():
    action = ActionMonitoringInput(
        action_id="A003",
        date_debut=date(2026, 7, 1),
        is_closed=True,
        frozen_age_days=42,
    )

    age = calculate_action_age(
        action=action,
        current_date=date(2026, 9, 20),
    )

    assert age == 42


def test_closed_action_without_frozen_age_returns_none():
    action = ActionMonitoringInput(
        action_id="A004",
        date_debut=date(2026, 7, 1),
        is_closed=True,
        frozen_age_days=None,
    )

    age = calculate_action_age(
        action=action,
        current_date=date(2026, 9, 20),
    )

    assert age is None


def test_unknown_closed_status_returns_none():
    action = ActionMonitoringInput(
        action_id="A005",
        date_debut=date(2026, 8, 1),
        is_closed=None,
    )

    age = calculate_action_age(
        action=action,
        current_date=date(2026, 9, 20),
    )

    assert age is None


def test_future_start_date_returns_none():
    action = ActionMonitoringInput(
        action_id="A006",
        date_debut=date(2026, 10, 1),
        is_closed=False,
    )

    age = calculate_action_age(
        action=action,
        current_date=date(2026, 9, 20),
    )

    assert age is None

@pytest.mark.parametrize(
    ("age_days", "expected_level"),
    [
        (0, EscalationLevel.NORMAL),
        (30, EscalationLevel.NORMAL),
        (31, EscalationLevel.ALERT),
        (60, EscalationLevel.ALERT),
        (61, EscalationLevel.CRITICAL),
        (90, EscalationLevel.CRITICAL),
        (91, EscalationLevel.MANAGEMENT_ESCALATION),
        (120, EscalationLevel.MANAGEMENT_ESCALATION),
    ],
)
def test_escalation_levels(age_days, expected_level):
    assert classify_escalation_level(age_days) == expected_level


def test_missing_age_returns_no_escalation_level():
    assert classify_escalation_level(None) is None


def test_negative_age_returns_no_escalation_level():
    assert classify_escalation_level(-1) is None