from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from src.common.config import RAW_DIR


def archive_raw_file(
    source_file: Path,
    campaign: str,
    batch_id: str,
) -> Path:
    """
    Copie le fichier source dans le Raw Layer
    en conservant une version immuable.
    """

    if not source_file.exists():
        raise FileNotFoundError(
            f"Source file not found: {source_file}"
        )

    ingestion_date = (
        datetime.now(timezone.utc)
        .date()
        .isoformat()
    )

    destination_dir = (
        RAW_DIR
        / campaign
        / ingestion_date
        / batch_id
    )

    destination_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination_file = (
        destination_dir
        / source_file.name
    )

    shutil.copy2(
        source_file,
        destination_file,
    )

    return destination_file