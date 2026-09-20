from __future__ import annotations

from datetime import date
from typing import Optional

from src.monitoring.models import ActionMonitoringInput
from src.monitoring.models import EscalationLevel


def calculate_action_age(
    action: ActionMonitoringInput,
    current_date: date,
) -> Optional[int]:
    """
    Calcule l'âge d'une action corrective.

    Règles métier :
    - si date_debut est absente, aucun âge n'est calculé ;
    - si l'action est ouverte / non clôturée :
        age_jours = current_date - date_debut ;
    - si l'action est clôturée :
        on conserve l'âge déjà figé ;
    - si le statut de clôture est inconnu :
        aucun âge n'est calculé ;
    - aucune valeur n'est inventée.
    """

    if action.date_debut is None:
        return None

    if action.is_closed is None:
        return None

    if action.is_closed is True:
        return action.frozen_age_days

    age_days = (current_date - action.date_debut).days

    if age_days < 0:
        return None

    return age_days


def classify_escalation_level(
    age_days: Optional[int],
) -> Optional[EscalationLevel]:
    """
    Classe une action corrective selon son âge.

    Seuils métier validés :
    - 0 à 30 jours   -> normal
    - 31 à 60 jours  -> alerte
    - 61 à 90 jours  -> critique
    - plus de 90     -> escalade management

    Si l'âge est indisponible, aucun niveau n'est produit.
    """

    if age_days is None:
        return None

    if age_days < 0:
        return None

    if age_days <= 30:
        return EscalationLevel.NORMAL

    if age_days <= 60:
        return EscalationLevel.ALERT

    if age_days <= 90:
        return EscalationLevel.CRITICAL

    return EscalationLevel.MANAGEMENT_ESCALATION