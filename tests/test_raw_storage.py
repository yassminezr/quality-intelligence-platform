from src.ingestion import raw_storage


def test_archive_raw_file(tmp_path, monkeypatch):
    source_file = tmp_path / "source.xlsx"

    source_file.write_text(
        "fake excel content",
        encoding="utf-8",
    )

    fake_raw_dir = tmp_path / "raw"

    monkeypatch.setattr(
        raw_storage,
        "RAW_DIR",
        fake_raw_dir,
    )

    archived_file = raw_storage.archive_raw_file(
        source_file=source_file,
        campaign="FY27",
        batch_id="batch-test-001",
    )

    assert archived_file.exists()

    assert archived_file.name == "source.xlsx"

    assert archived_file.read_text(
        encoding="utf-8"
    ) == "fake excel content"