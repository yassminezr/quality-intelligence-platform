from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.profiling.column_mapping import COLUMN_MAPPING


def load_schema_comparison(schema_path: Path) -> dict:
    """
    Charge le rapport produit par compare_audit_schemas.py.
    """

    if not schema_path.exists():
        raise FileNotFoundError(
            f"Schema comparison file not found: {schema_path}"
        )

    with schema_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def get_observed_columns(schema_report: dict) -> set[str]:
    """
    Récupère toutes les colonnes observées dans les feuilles d'audit.
    """

    observed_columns = set()

    for variant in schema_report["schema_variants"]:
        observed_columns.update(variant["columns"])

    return observed_columns


def validate_mapping(
    observed_columns: set[str],
    column_mapping: dict[str, str],
) -> dict:
    """
    Compare les colonnes Excel observées avec le mapping canonique.
    """

    mapped_source_columns = set(column_mapping.keys())

    mapped_columns = sorted(
        observed_columns & mapped_source_columns
    )

    unmapped_columns = sorted(
        observed_columns - mapped_source_columns
    )

    unused_mappings = sorted(
        mapped_source_columns - observed_columns
    )

    canonical_columns = sorted(
        {
            column_mapping[column]
            for column in mapped_columns
        }
    )

    return {
        "observed_column_count": len(observed_columns),
        "mapped_column_count": len(mapped_columns),
        "unmapped_column_count": len(unmapped_columns),
        "canonical_column_count": len(canonical_columns),
        "mapped_columns": mapped_columns,
        "unmapped_columns": unmapped_columns,
        "unused_mappings": unused_mappings,
        "canonical_columns": canonical_columns,
    }


def save_report(
    report: dict,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Validate Excel column mapping coverage."
    )

    parser.add_argument(
        "--input",
        default=Path(
            "data/profiling/schema_comparison.json"
        ),
        type=Path,
    )

    parser.add_argument(
        "--output",
        default=Path(
            "data/profiling/column_mapping_validation.json"
        ),
        type=Path,
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    schema_report = load_schema_comparison(args.input)

    observed_columns = get_observed_columns(
        schema_report
    )

    report = validate_mapping(
        observed_columns=observed_columns,
        column_mapping=COLUMN_MAPPING,
    )

    save_report(
        report=report,
        output_path=args.output,
    )

    print("Column mapping validation completed.")
    print(
        f"Observed columns: "
        f"{report['observed_column_count']}"
    )
    print(
        f"Mapped columns: "
        f"{report['mapped_column_count']}"
    )
    print(
        f"Unmapped columns: "
        f"{report['unmapped_column_count']}"
    )
    print(
        f"Canonical columns produced: "
        f"{report['canonical_column_count']}"
    )

    if report["unmapped_columns"]:
        print("\nColumns requiring review:")

        for column in report["unmapped_columns"]:
            print(f"- {column}")


if __name__ == "__main__":
    main()