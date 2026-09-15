from src.modeling.load_audit_core import (
    propose_audit_status,
)
from src.modeling.load_iso_reference import (
    is_valid_iso_clause,
)
from src.modeling.history_utils import (
    values_changed,
)


def test_propose_audit_status():
    assert propose_audit_status(0) == "non_audite"
    assert propose_audit_status(30) == "en_cours"
    assert propose_audit_status(65) == "a_valider"
    assert propose_audit_status(80) == "audite"


def test_iso_clause_filter():
    assert is_valid_iso_clause("4.1") is True
    assert is_valid_iso_clause("7.1.1") is True
    assert is_valid_iso_clause("10.2") is True

    assert is_valid_iso_clause("Leadership") is False
    assert is_valid_iso_clause("Support") is False
    assert is_valid_iso_clause("Libellé") is False


def test_history_detects_real_change():
    current = (
        3,
        "Stable",
        "Constat A",
    )

    same = (
        3,
        "Stable",
        "Constat A",
    )

    changed = (
        4,
        "Proactif",
        "Constat A",
    )

    assert values_changed(
        current,
        same,
    ) is False

    assert values_changed(
        current,
        changed,
    ) is True