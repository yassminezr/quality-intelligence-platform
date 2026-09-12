import pytest

from src.ingestion.incoming_file import (
    find_incoming_excel,
)


def test_one_excel_file_is_selected(tmp_path):
    incoming_dir = tmp_path / "incoming"
    incoming_dir.mkdir()

    file_path = incoming_dir / "QHC_test.xlsx"
    file_path.write_text(
        "fake excel",
        encoding="utf-8",
    )

    result = find_incoming_excel(
        incoming_dir
    )

    assert result == file_path


def test_no_excel_file_raises_error(tmp_path):
    incoming_dir = tmp_path / "incoming"
    incoming_dir.mkdir()

    with pytest.raises(
        FileNotFoundError
    ):
        find_incoming_excel(
            incoming_dir
        )


def test_multiple_excel_files_raise_error(
    tmp_path,
):
    incoming_dir = tmp_path / "incoming"
    incoming_dir.mkdir()

    (
        incoming_dir
        / "file_1.xlsx"
    ).write_text(
        "test",
        encoding="utf-8",
    )

    (
        incoming_dir
        / "file_2.xlsx"
    ).write_text(
        "test",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError
    ):
        find_incoming_excel(
            incoming_dir
        )