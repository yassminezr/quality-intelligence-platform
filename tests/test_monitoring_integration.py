from datetime import date

from src.monitoring.models import (
    ActionMonitoringInput,
    EscalationLevel,
)
from src.monitoring.rules import (
    calculate_action_age,
    classify_escalation_level,
)


def test_action_without_start_date_has_no_age():
    action = ActionMonitoringInput(
        action_id="1",
        date_debut=None,
        is_closed=False,
    )

    age = calculate_action_age(
        action=action,
        current_date=date(2026, 9, 20),
    )

    assert age is None

    level = classify_escalation_level(age)

    assert level is None


def test_closed_action_keeps_frozen_age():
    action = ActionMonitoringInput(
        action_id="2",
        date_debut=date(2026, 1, 1),
        is_closed=True,
        frozen_age_days=45,
    )

    age = calculate_action_age(
        action=action,
        current_date=date(2026, 9, 20),
    )

    assert age == 45

    level = classify_escalation_level(age)

    assert level == EscalationLevel.ALERT


def test_open_action_moves_from_alert_to_critical():
    action = ActionMonitoringInput(
        action_id="3",
        date_debut=date(2026, 8, 1),
        is_closed=False,
    )

    age_alert = calculate_action_age(
        action=action,
        current_date=date(2026, 9, 20),
    )

    level_alert = classify_escalation_level(age_alert)

    assert age_alert == 50
    assert level_alert == EscalationLevel.ALERT

    age_critical = calculate_action_age(
        action=action,
        current_date=date(2026, 10, 2),
    )

    level_critical = classify_escalation_level(
        age_critical
    )

    assert age_critical == 62
    assert level_critical == EscalationLevel.CRITICAL


def test_same_level_does_not_change_business_classification():
    action = ActionMonitoringInput(
        action_id="4",
        date_debut=date(2026, 9, 1),
        is_closed=False,
    )

    age_day_1 = calculate_action_age(
        action=action,
        current_date=date(2026, 9, 20),
    )

    age_day_2 = calculate_action_age(
        action=action,
        current_date=date(2026, 9, 21),
    )

    level_day_1 = classify_escalation_level(age_day_1)
    level_day_2 = classify_escalation_level(age_day_2)

    assert level_day_1 == EscalationLevel.NORMAL
    assert level_day_2 == EscalationLevel.NORMAL


def test_escalation_boundaries():
    assert classify_escalation_level(30) == EscalationLevel.NORMAL
    assert classify_escalation_level(31) == EscalationLevel.ALERT
    assert classify_escalation_level(60) == EscalationLevel.ALERT
    assert classify_escalation_level(61) == EscalationLevel.CRITICAL
    assert classify_escalation_level(90) == EscalationLevel.CRITICAL
    assert (
        classify_escalation_level(91)
        == EscalationLevel.MANAGEMENT_ESCALATION
    )