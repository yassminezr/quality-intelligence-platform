from __future__ import annotations

from pathlib import Path


def find_incoming_excel(
    incoming_dir: Path,
) -> Path:
    """
    Recherche le fichier Excel à ingérer
    dans le dossier incoming.

    Règle actuelle :
    - exactement un fichier .xlsx doit être présent ;
    - sinon le pipeline s'arrête.
    """

    if not incoming_dir.exists():
        raise FileNotFoundError(
            f"Incoming directory not found: {incoming_dir}"
        )

    excel_files = list(
        incoming_dir.glob("*.xlsx")
    )

    if len(excel_files) == 0:
        raise FileNotFoundError(
            "No Excel file found in incoming directory."
        )

    if len(excel_files) > 1:
        raise ValueError(
            "Multiple Excel files found in incoming directory. "
            "Expected exactly one."
        )

    return excel_files[0]