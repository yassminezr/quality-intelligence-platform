from __future__ import annotations

from typing import List

from src.monitoring.notifications.formatter import AlertMessage
from src.monitoring.notifications.llm_writer import LLMWriter


class AlertWritingService:
    """
    Applique éventuellement une reformulation LLM
    aux messages déjà générés déterministiquement.
    """

    def __init__(self, writer: LLMWriter):
        self.writer = writer

    def rewrite_messages(
        self,
        messages: List[AlertMessage],
    ) -> List[AlertMessage]:
        rewritten_messages = []

        for message in messages:
            try:
                rewritten = self.writer.rewrite(message)
                rewritten_messages.append(rewritten)

            except Exception:
                # Le monitoring ne doit jamais échouer
                # parce que le LLM est indisponible.
                rewritten_messages.append(message)

        return rewritten_messages