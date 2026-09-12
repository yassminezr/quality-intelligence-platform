import json
from pathlib import Path

from openpyxl import Workbook

from src.ingestion import ingestion_batch
from src.ingestion import raw_storage
from src.ingestion.run_ingestion import run_ingestion
from src.common import config


def create_test_workbook(file_path: Path) -> None:
    """
    Crée un petit workbook QHC contrôlé
    avec une seule feuille d'audit.
    """

    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = "Test Account"

    headers = [
        "N°",
        "Clause ISO",
        "Intitulé ISO",
        "Libellé Terrain",
        "Ce qu'il faut contrôler",
        "Constat de l'Auditeur",
        "Catégorie Finding",
        "Niveau de maturité",
        "Score (1-5)",
    ]

    worksheet.append(headers)

    worksheet.append(
        [
            1,
            "4.1",
            "Contexte de l'organisation",
            "Compréhension du contexte",
            "Vérifier le contexte",
            "Conforme",
            "NA",
            "Totalement en place/Proactif",
            4,
        ]
    )

    workbook.save(file_path)


def test_full_ingestion_pipeline(
    tmp_path,
    monkeypatch,
):
    # 1. Créer les dossiers temporaires
    raw_dir = tmp_path / "raw"
    standardized_dir = tmp_path / "standardized"

    metadata_dir = raw_dir / "_metadata"
    batch_registry = (
        metadata_dir
        / "ingestion_batches.jsonl"
    )

    # 2. Rediriger les chemins utilisés
    # par le pipeline vers tmp_path
    monkeypatch.setattr(
        raw_storage,
        "RAW_DIR",
        raw_dir,
    )

    monkeypatch.setattr(
        ingestion_batch,
        "METADATA_DIR",
        metadata_dir,
    )

    monkeypatch.setattr(
        ingestion_batch,
        "BATCH_REGISTRY",
        batch_registry,
    )

    # run_ingestion a importé STANDARDIZED_DIR
    # directement, donc on modifie la variable
    # dans son propre module.
    import src.ingestion.run_ingestion as run_module

    monkeypatch.setattr(
        run_module,
        "STANDARDIZED_DIR",
        standardized_dir,
    )

    # 3. Créer un workbook de test
    source_file = (
        tmp_path
        / "QHC_test.xlsx"
    )

    create_test_workbook(
        source_file
    )

    # 4. Exécuter le pipeline
    run_ingestion(
        source_file=source_file,
        campaign="FY27",
    )

    # 5. Vérifier que le registre existe
    assert batch_registry.exists()

    # 6. Lire les événements du batch
    with batch_registry.open(
        "r",
        encoding="utf-8",
    ) as file:
        batches = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    assert len(batches) == 2

    assert batches[0]["status"] == "STARTED"
    assert batches[1]["status"] == "SUCCESS"

    batch_id = batches[1]["batch_id"]

    # 7. Vérifier le fichier raw
    raw_files = list(
        (
            raw_dir
            / "FY27"
        ).rglob(
            "QHC_test.xlsx"
        )
    )

    assert len(raw_files) == 1

    # 8. Vérifier les sorties standardisées
    batch_output_dir = (
        standardized_dir
        / "FY27"
        / batch_id
    )

    inventory_file = (
        batch_output_dir
        / "workbook_inventory.json"
    )

    standardized_file = (
        batch_output_dir
        / "standardized_audits.csv"
    )

    assert inventory_file.exists()
    assert standardized_file.exists()

    # 9. Vérifier l'inventaire
    with inventory_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        inventory = json.load(file)

    assert inventory["sheet_count"] == 1

    audit_sheets = [
        sheet
        for sheet in inventory["sheets"]
        if sheet["sheet_type"]
        == "audit_account"
    ]

    assert len(audit_sheets) == 1

    assert (
        audit_sheets[0]["sheet_name"]
        == "Test Account"
    )

    # 10. Vérifier le CSV
    csv_content = standardized_file.read_text(
        encoding="utf-8-sig"
    )

    assert "Test Account" in csv_content
    assert "4.1" in csv_content
    assert "NA" in csv_content