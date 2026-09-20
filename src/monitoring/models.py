from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class EscalationLevel(str, Enum):
    """
    Niveaux métier validés pour le monitoring
    des actions correctives.
    """

    NORMAL = "normal"
    ALERT = "alerte"
    CRITICAL = "critique"
    MANAGEMENT_ESCALATION = "escalade_management"


@dataclass(frozen=True)
class ActionMonitoringInput:
    """
    Données nécessaires au monitoring d'une action corrective.
    """

    action_id: str

    date_debut: Optional[date]

    is_closed: Optional[bool]

    frozen_age_days: Optional[int] = None

    account_name: Optional[str] = None

    action_text: Optional[str] = None

    responsable: Optional[str] = None

    statut: Optional[str] = None

@dataclass(frozen=True)
class ActionMonitoringResult:
    """
    Résultat produit par le moteur déterministe.
    """

    action_id: str

    age_jours: Optional[int]

    niveau_escalade: Optional[EscalationLevel]

    date_evaluation: date

@dataclass(frozen=True)
class MonitoringEvent:
    """
    Représente un changement détecté par le moteur de monitoring.
    """

    action: ActionMonitoringInput

    result: ActionMonitoringResult

    previous_level: Optional[str]

    current_level: Optional[str]