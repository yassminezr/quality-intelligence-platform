from src.monitoring.notifications.formatter import AlertMessage
from src.monitoring.notifications.llm_writer import (
    DeterministicFallbackWriter,
)
from src.monitoring.notifications.writing_service import (
    AlertWritingService,
)


class FakeLLMWriter:
    def rewrite(self, message: AlertMessage) -> AlertMessage:
        return AlertMessage(
            subject=f"{message.subject} - reformulé",
            body=f"Message professionnel : {message.body}",
        )


class FailingLLMWriter:
    def rewrite(self, message: AlertMessage) -> AlertMessage:
        raise RuntimeError("LLM indisponible")


def test_llm_writer_can_rewrite_message():
    original = AlertMessage(
        subject="Action critique",
        body="Action âgée de 67 jours.",
    )

    service = AlertWritingService(
        writer=FakeLLMWriter(),
    )

    messages = service.rewrite_messages([original])

    assert len(messages) == 1
    assert messages[0].subject == "Action critique - reformulé"
    assert "Message professionnel" in messages[0].body


def test_llm_failure_keeps_deterministic_message():
    original = AlertMessage(
        subject="Action critique",
        body="Action âgée de 67 jours.",
    )

    service = AlertWritingService(
        writer=FailingLLMWriter(),
    )

    messages = service.rewrite_messages([original])

    assert len(messages) == 1
    assert messages[0] == original


def test_deterministic_fallback_writer_returns_same_message():
    original = AlertMessage(
        subject="Action critique",
        body="Action âgée de 67 jours.",
    )

    writer = DeterministicFallbackWriter()

    rewritten = writer.rewrite(original)

    assert rewritten == original


def test_no_messages_returns_empty_list():
    service = AlertWritingService(
        writer=FakeLLMWriter(),
    )

    messages = service.rewrite_messages([])

    assert messages == []