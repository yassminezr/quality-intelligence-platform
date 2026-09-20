from src.monitoring.notifications.recipient_resolver import (
    RecipientResolver,
)


def test_resolve_configured_recipients():
    resolver = RecipientResolver(
        recipients_by_level={
            "alerte": [
                "quality@example.com",
            ],
            "critique": [
                "quality@example.com",
                "manager@example.com",
            ],
        }
    )

    recipients = resolver.resolve(
        escalation_level="critique",
    )

    assert recipients == [
        "quality@example.com",
        "manager@example.com",
    ]


def test_unknown_level_returns_empty_list():
    resolver = RecipientResolver(
        recipients_by_level={}
    )

    recipients = resolver.resolve(
        escalation_level="critique",
    )

    assert recipients == []


def test_none_level_returns_empty_list():
    resolver = RecipientResolver(
        recipients_by_level={}
    )

    recipients = resolver.resolve(
        escalation_level=None,
    )

    assert recipients == []