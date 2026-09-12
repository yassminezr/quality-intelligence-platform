from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from src.common.config import RAW_DIR


METADATA_DIR = RAW_DIR / "_metadata"
BATCH_REGISTRY = METADATA_DIR / "ingestion_batches.jsonl"


@dataclass
class IngestionBatch:
    batch_id: str
    campaign: str
    source_file: str
    file_hash: str
    ingestion_timestamp: str
    status: str


def create_batch(
    campaign: str,
    source_file: Path,
    file_hash: str,
) -> IngestionBatch:
    """
    Crée un nouveau batch d'ingestion.
    """

    batch = IngestionBatch(
        batch_id=str(uuid.uuid4()),
        campaign=campaign,
        source_file=source_file.name,
        file_hash=file_hash,
        ingestion_timestamp=datetime.now(timezone.utc).isoformat(),
        status="STARTED",
    )

    return batch


def save_batch(batch: IngestionBatch) -> None:
    """
    Ajoute le batch au registre local JSONL.
    """

    METADATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with BATCH_REGISTRY.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                asdict(batch),
                ensure_ascii=False,
            )
            + "\n"
        )

def hash_already_ingested(
    file_hash: str,
) -> bool:
    """
    Vérifie si un fichier possédant le même hash
    existe déjà dans le registre d'ingestion.
    """

    if not BATCH_REGISTRY.exists():
        return False

    with BATCH_REGISTRY.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            if not line.strip():
                continue

            batch = json.loads(line)

            if (
                batch.get("file_hash") == file_hash
                and batch.get("status") == "SUCCESS"
            ):
                return True

    return False