from __future__ import annotations

from dataclasses import dataclass

from src.monitoring.models import (
    ActionMonitoringInput,
    ActionMonitoringResult,
)


@dataclass(frozen=True)
class AlertMessage:
    """
    Contenu d'un message de monitoring.

    Aucun envoi n'est effectué ici.
    """

    subject: str
    body: str


def _safe_value(value: object) -> str:
    """
    Retourne une représentation lisible d'une valeur.

    Une donnée absente reste explicitement indiquée comme non renseignée.
    """

    if value is None:
        return "Non renseigné"

    text = str(value).strip()

    if not text:
        return "Non renseigné"

    return text


def build_alert_message(
    action: ActionMonitoringInput,
    result: ActionMonitoringResult,
) -> AlertMessage:
    """
    Génère déterministiquement le contenu du message
    associé à un résultat de monitoring.

    Cette fonction ne décide pas si le message doit être envoyé.
    """

    account_name = _safe_value(action.account_name)
    responsable = _safe_value(action.responsable)
    action_text = _safe_value(action.action_text)
    statut = _safe_value(action.statut)

    age_jours = (
        str(result.age_jours)
        if result.age_jours is not None
        else "Non calculable"
    )

    niveau = (
        result.niveau_escalade.value
        if result.niveau_escalade is not None
        else "Non déterminé"
    )

    subject = (
        f"[QIP] Action corrective - "
        f"{niveau.replace('_', ' ').title()} - "
        f"{account_name}"
    )

    body = (
        "Suivi d'une action corrective\n\n"
        f"Action ID : {action.action_id}\n"
        f"Compte : {account_name}\n"
        f"Responsable : {responsable}\n"
        f"Statut : {statut}\n"
        f"Âge : {age_jours} jours\n"
        f"Niveau : {niveau}\n\n"
        f"Action corrective :\n{action_text}"
    )

    return AlertMessage(
        subject=subject,
        body=body,
    )