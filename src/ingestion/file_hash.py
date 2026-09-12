from __future__ import annotations

import hashlib
from pathlib import Path


def calculate_sha256(file_path: Path) -> str:
    """
    Calcule l'empreinte SHA-256 d'un fichier.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        while chunk := file.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()