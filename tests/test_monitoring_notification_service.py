from datetime import date

from src.monitoring.models import (
    ActionMonitoringInput,
    ActionMonitoringResult,
    EscalationLevel,
    MonitoringEvent,
)
from src.monitoring.notifications.formatter import AlertMessage
from src.monitoring.notifications.notification_service import (
    NotificationService,
)
from src.monitoring.notifications.recipient_resolver import (
    RecipientResolver,
)


class FakeEmailSender:
    def __init__(self):
        self.sent = []

    def send(self, recipient, message):
        self.sent.append(
            {
                "recipient": recipient,
                "message": message,
            }
        )


class FailingEmailSender:
    def send(self, recipient, message):
        raise RuntimeError("SMTP indisponible")


def build_event():
    action = ActionMonitoringInput(
        action_id="1",
        date_debut=date(2026, 7, 15),
        is_closed=False,
        account_name="Min. Intérieur",
        action_text="Formaliser le suivi.",
        responsable="Mohamed",
        statut="En cours",
    )

    result = ActionMonitoringResult(
        action_id="1",
        age_jours=67,
        niveau_escalade=EscalationLevel.CRITICAL,
        date_evaluation=date(2026, 9, 20),
    )

    return MonitoringEvent(
        action=action,
        result=result,
        previous_level="alerte",
        current_level="critique",
    )


def test_notification_is_sent_to_configured_recipients():
    resolver = RecipientResolver(
        recipients_by_level={
            "critique": [
                "quality@example.com",
                "manager@example.com",
            ]
        }
    )

    sender = FakeEmailSender()

    service = NotificationService(
        recipient_resolver=resolver,
        email_sender=sender,
    )

    event = build_event()

    message = AlertMessage(
        subject="[QIP] Action critique",
        body="Message de test",
    )

    results = service.send_notifications(
        events=[event],
        messages=[message],
    )

    assert len(sender.sent) == 2
    assert len(results) == 2

    assert results[0].success is True
    assert results[1].success is True

    assert sender.sent[0]["recipient"] == "quality@example.com"
    assert sender.sent[1]["recipient"] == "manager@example.com"


def test_no_recipient_means_no_email():
    resolver = RecipientResolver(
        recipients_by_level={}
    )

    sender = FakeEmailSender()

    service = NotificationService(
        recipient_resolver=resolver,
        email_sender=sender,
    )

    results = service.send_notifications(
        events=[build_event()],
        messages=[
            AlertMessage(
                subject="Test",
                body="Test",
            )
        ],
    )

    assert sender.sent == []
    assert results == []


def test_email_failure_is_captured():
    resolver = RecipientResolver(
        recipients_by_level={
            "critique": [
                "quality@example.com",
            ]
        }
    )

    service = NotificationService(
        recipient_resolver=resolver,
        email_sender=FailingEmailSender(),
    )

    results = service.send_notifications(
        events=[build_event()],
        messages=[
            AlertMessage(
                subject="Test",
                body="Test",
            )
        ],
    )

    assert len(results) == 1

    assert results[0].success is False
    assert results[0].recipient == "quality@example.com"
    assert results[0].error == "SMTP indisponible"


def test_mismatched_events_and_messages_raises_error():
    resolver = RecipientResolver(
        recipients_by_level={}
    )

    sender = FakeEmailSender()

    service = NotificationService(
        recipient_resolver=resolver,
        email_sender=sender,
    )

    try:
        service.send_notifications(
            events=[build_event()],
            messages=[],
        )

        assert False

    except ValueError:
        assert True