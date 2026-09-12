import json

from src.ingestion import ingestion_batch


def test_successful_hash_is_detected(
    tmp_path,
    monkeypatch,
):
    registry = (
        tmp_path
        / "ingestion_batches.jsonl"
    )

    successful_batch = {
        "batch_id": "batch-001",
        "campaign": "FY27",
        "source_file": "QHC.xlsx",
        "file_hash": "abc123",
        "ingestion_timestamp": "2026-09-09",
        "status": "SUCCESS",
    }

    registry.write_text(
        json.dumps(successful_batch) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        ingestion_batch,
        "BATCH_REGISTRY",
        registry,
    )

    assert (
        ingestion_batch.hash_already_ingested(
            "abc123"
        )
        is True
    )


def test_failed_hash_can_be_reprocessed(
    tmp_path,
    monkeypatch,
):
    registry = (
        tmp_path
        / "ingestion_batches.jsonl"
    )

    failed_batch = {
        "batch_id": "batch-002",
        "campaign": "FY27",
        "source_file": "QHC.xlsx",
        "file_hash": "xyz789",
        "ingestion_timestamp": "2026-09-09",
        "status": "FAILED",
    }

    registry.write_text(
        json.dumps(failed_batch) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        ingestion_batch,
        "BATCH_REGISTRY",
        registry,
    )

    assert (
        ingestion_batch.hash_already_ingested(
            "xyz789"
        )
        is False
    )