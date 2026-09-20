from __future__ import annotations

from typing import Dict, List


class RecipientResolver:
    """
    Résout les destinataires à partir d'une configuration externe.

    Aucune règle métier ni adresse email n'est codée en dur.
    """

    def __init__(
        self,
        recipients_by_level: Dict[str, List[str]],
    ):
        self.recipients_by_level = recipients_by_level

    def resolve(
        self,
        escalation_level: str | None,
    ) -> List[str]:
        """
        Retourne les destinataires configurés
        pour un niveau donné.

        Si aucun destinataire n'est configuré,
        retourne une liste vide.
        """

        if escalation_level is None:
            return []

        return self.recipients_by_level.get(
            escalation_level,
            [],
        )