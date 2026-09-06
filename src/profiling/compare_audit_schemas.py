from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def load_inventory(inventory_path: Path) -> dict:
    """
    Charge l'inventaire produit par workbook_inventory.py.
    """

    if not inventory_path.exists():
        raise FileNotFoundError(
            f"Inventory file not found: {inventory_path}"
        )

    with inventory_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def get_audit_sheets(inventory: dict) -> list[dict]:
    """
    Retourne uniquement les feuilles classées comme feuilles d'audit.
    """

    return [
        sheet
        for sheet in inventory["sheets"]
        if sheet["sheet_type"] == "audit_account"
    ]


def find_common_columns(audit_sheets: list[dict]) -> list[str]:
    """
    Identifie les colonnes présentes dans toutes les feuilles d'audit.
    """

    if not audit_sheets:
        return []

    common_columns = set(audit_sheets[0]["headers"])

    for sheet in audit_sheets[1:]:
        common_columns &= set(sheet["headers"])

    return sorted(common_columns)


def find_all_columns(audit_sheets: list[dict]) -> list[str]:
    """
    Identifie toutes les colonnes observées au moins une fois.
    """

    all_columns = set()

    for sheet in audit_sheets:
        all_columns.update(sheet["headers"])

    return sorted(all_columns)


def group_schema_variants(
    audit_sheets: list[dict],
) -> list[dict]:
    """
    Regroupe les feuilles ayant exactement la même structure.
    """

    groups = defaultdict(list)

    for sheet in audit_sheets:
        schema = tuple(sheet["headers"])
        groups[schema].append(sheet["sheet_name"])

    variants = []

    for variant_number, (schema, sheet_names) in enumerate(
        groups.items(),
        start=1,
    ):
        variants.append(
            {
                "variant_id": f"variant_{variant_number}",
                "sheet_count": len(sheet_names),
                "sheets": sheet_names,
                "columns": list(schema),
            }
        )

    return variants


def compare_each_sheet(
    audit_sheets: list[dict],
    common_columns: list[str],
    all_columns: list[str],
) -> list[dict]:
    """
    Pour chaque feuille, identifie les colonnes spécifiques
    et les colonnes absentes.
    """

    common_set = set(common_columns)
    all_columns_set = set(all_columns)

    comparisons = []

    for sheet in audit_sheets:
        sheet_columns = set(sheet["headers"])

        specific_columns = sorted(
            sheet_columns - common_set
        )

        missing_columns = sorted(
            all_columns_set - sheet_columns
        )

        comparisons.append(
            {
                "sheet_name": sheet["sheet_name"],
                "column_count": len(sheet["headers"]),
                "specific_columns": specific_columns,
                "missing_columns": missing_columns,
            }
        )

    return comparisons


def build_schema_comparison(inventory: dict) -> dict:
    """
    Construit le rapport global de comparaison des schémas.
    """

    audit_sheets = get_audit_sheets(inventory)

    common_columns = find_common_columns(audit_sheets)
    all_columns = find_all_columns(audit_sheets)

    schema_variants = group_schema_variants(
        audit_sheets
    )

    sheet_comparisons = compare_each_sheet(
        audit_sheets=audit_sheets,
        common_columns=common_columns,
        all_columns=all_columns,
    )

    return {
        "audit_sheet_count": len(audit_sheets),
        "common_column_count": len(common_columns),
        "all_observed_column_count": len(all_columns),
        "schema_variant_count": len(schema_variants),
        "common_columns": common_columns,
        "schema_variants": schema_variants,
        "sheet_comparisons": sheet_comparisons,
    }


def save_report(
    report: dict,
    output_path: Path,
) -> None:
    """
    Sauvegarde le rapport de comparaison en JSON.
    """

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
        description="Compare audit sheet schemas."
    )

    parser.add_argument(
        "--input",
        default=Path(
            "data/profiling/workbook_inventory.json"
        ),
        type=Path,
        help="Workbook inventory JSON.",
    )

    parser.add_argument(
        "--output",
        default=Path(
            "data/profiling/schema_comparison.json"
        ),
        type=Path,
        help="Generated schema comparison report.",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    inventory = load_inventory(args.input)

    report = build_schema_comparison(inventory)

    save_report(
        report=report,
        output_path=args.output,
    )

    print("Audit schema comparison completed.")
    print(
        f"Audit sheets detected: "
        f"{report['audit_sheet_count']}"
    )
    print(
        f"Schema variants detected: "
        f"{report['schema_variant_count']}"
    )
    print(
        f"Common columns: "
        f"{report['common_column_count']}"
    )
    print(
        f"All observed columns: "
        f"{report['all_observed_column_count']}"
    )
    print(f"Report saved to: {args.output}")


if __name__ == "__main__":
    main()