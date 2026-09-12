from src.ingestion.file_hash import calculate_sha256


def test_same_file_produces_same_hash(tmp_path):
    file_path = tmp_path / "test.txt"

    file_path.write_text(
        "quality intelligence platform",
        encoding="utf-8",
    )

    hash_1 = calculate_sha256(file_path)
    hash_2 = calculate_sha256(file_path)

    assert hash_1 == hash_2


def test_modified_file_produces_different_hash(tmp_path):
    file_path = tmp_path / "test.txt"

    file_path.write_text(
        "version 1",
        encoding="utf-8",
    )

    hash_1 = calculate_sha256(file_path)

    file_path.write_text(
        "version 2",
        encoding="utf-8",
    )

    hash_2 = calculate_sha256(file_path)

    assert hash_1 != hash_2