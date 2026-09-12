from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DQSeverity(str, Enum):
    """
    Niveau de sévérité d'une anomalie Data Quality.
    """

    WARNING = "WARNING"
    ERROR = "ERROR"
    BLOCKING = "BLOCKING"


@dataclass
class DQIssue:
    """
    Représente une anomalie détectée
    par une règle Data Quality.
    """

    rule_id: str
    severity: DQSeverity
    message: str

    source_file: str | None = None
    source_sheet: str | None = None
    source_row_number: str | None = None


@dataclass
class DQReport:
    """
    Résultat global d'une exécution Data Quality.
    """

    issues: list[DQIssue]

    @property
    def total_issues(self) -> int:
        return len(self.issues)

    @property
    def warning_count(self) -> int:
        return sum(
            issue.severity == DQSeverity.WARNING
            for issue in self.issues
        )

    @property
    def error_count(self) -> int:
        return sum(
            issue.severity == DQSeverity.ERROR
            for issue in self.issues
        )

    @property
    def blocking_count(self) -> int:
        return sum(
            issue.severity == DQSeverity.BLOCKING
            for issue in self.issues
        )

    @property
    def has_blocking_issues(self) -> bool:
        return self.blocking_count > 0