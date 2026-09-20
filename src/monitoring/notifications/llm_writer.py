from __future__ import annotations

import os
from typing import Protocol

from openai import OpenAI

from src.monitoring.notifications.formatter import AlertMessage


class LLMWriter(Protocol):
    """
    Contrat pour un composant capable de reformuler
    un message d'alerte.

    Le LLM ne prend aucune décision métier.
    """

    def rewrite(self, message: AlertMessage) -> AlertMessage:
        ...


class DeterministicFallbackWriter:
    """
    Retourne le message déterministe sans modification.
    """

    def rewrite(self, message: AlertMessage) -> AlertMessage:
        return message


class OpenAIAlertWriter:
    """
    Utilise OpenAI uniquement pour reformuler
    le corps d'un message déjà produit par le moteur déterministe.
    """

    def __init__(
        self,
        client: OpenAI | None = None,
        model: str | None = None,
    ):
        self.client = client or OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.model = model or os.getenv(
            "OPENAI_MODEL",
            "gpt-6-astra",
        )

    def rewrite(self, message: AlertMessage) -> AlertMessage:
        """
        Reformule uniquement le corps du message.

        Le sujet déterministe est conservé tel quel.
        """

        response = self.client.responses.create(
            model=self.model,
            instructions=(
                "Tu es un assistant de rédaction professionnelle "
                "pour une plateforme de suivi qualité. "
                "Tu dois uniquement reformuler le message fourni. "
                "Ne modifie aucun chiffre, nom, statut, niveau "
                "d'escalade, identifiant ou information métier. "
                "N'invente aucune information. "
                "Ne décide jamais du niveau de criticité. "
                "Rédige un message professionnel, concis et clair "
                "en français. "
                "Retourne uniquement le corps final du message."
            ),
            input=message.body,
        )

        rewritten_body = response.output_text.strip()

        if not rewritten_body:
            return message

        return AlertMessage(
            subject=message.subject,
            body=rewritten_body,
        )