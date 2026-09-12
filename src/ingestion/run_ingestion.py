from __future__ import annotations

from pathlib import Path

from src.common.logger import get_logger
from src.common.config import (
    CURRENT_CAMPAIGN,
    STANDARDIZED_DIR,
)
from src.ingestion.file_hash import calculate_sha256
from src.ingestion.ingestion_batch import (
    create_batch,
    hash_already_ingested,
    save_batch,
)
from src.ingestion.raw_storage import archive_raw_file
from src.profiling.standardize_audits import (
    standardize_workbook,
    save_standardized_csv,
)
from src.profiling.workbook_inventory import (
    profile_workbook,
    save_inventory,
)


logger = get_logger(__name__)


def run_ingestion(
    source_file: Path,
    campaign: str,
) -> str | None:
    """
    Exécute le pipeline d'ingestion complet
    d'un fichier Excel source.
    """

    logger.info("Ingestion started.")

    logger.info(
        "Source file: %s",
        source_file,
    )

    # 1. Vérifier que le fichier existe
    if not source_file.exists():
        raise FileNotFoundError(
            f"Source file not found: {source_file}"
        )

    # 2. Calculer le hash SHA-256
    file_hash = calculate_sha256(
        source_file
    )

    logger.info(
        "SHA-256 calculated: %s",
        file_hash,
    )

    # 3. Vérifier si le fichier a déjà été
    # ingéré avec succès
    if hash_already_ingested(file_hash):
        logger.warning(
            "File already ingested successfully. "
            "Ingestion skipped."
        )
        return None

    # 4. Créer un nouveau batch
    batch = create_batch(
        campaign=campaign,
        source_file=source_file,
        file_hash=file_hash,
    )

    save_batch(batch)

    logger.info(
        "Batch created: %s",
        batch.batch_id,
    )

    try:

        # 5. Archiver le fichier source
        # dans le Raw Layer
        archived_file = archive_raw_file(
            source_file=source_file,
            campaign=campaign,
            batch_id=batch.batch_id,
        )

        logger.info(
            "Raw file archived: %s",
            archived_file,
        )

        # 6. Préparer le dossier
        # standardized du batch
        standardized_dir = (
            STANDARDIZED_DIR
            / campaign
            / batch.batch_id
        )

        standardized_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # 7. Définir les fichiers de sortie
        inventory_file = (
            standardized_dir
            / "workbook_inventory.json"
        )

        standardized_file = (
            standardized_dir
            / "standardized_audits.csv"
        )

        # 8. Générer dynamiquement
        # l'inventaire du workbook RAW
        inventory = profile_workbook(
            archived_file
        )

        save_inventory(
            inventory=inventory,
            output_path=inventory_file,
        )

        logger.info(
            "Workbook inventory generated: %s",
            inventory_file,
        )

        logger.info(
            "Sheets detected: %s",
            inventory["sheet_count"],
        )

        audit_sheet_count = sum(
            1
            for sheet in inventory["sheets"]
            if sheet["sheet_type"]
            == "audit_account"
        )

        logger.info(
            "Audit sheets detected: %s",
            audit_sheet_count,
        )

        # 9. Standardiser le workbook
        # en utilisant SON propre inventaire
        rows = standardize_workbook(
            excel_path=archived_file,
            inventory_path=inventory_file,
        )

        # 10. Sauvegarder
        # les données standardisées
        save_standardized_csv(
            rows=rows,
            output_path=standardized_file,
        )

        logger.info(
            "Standardized rows: %s",
            len(rows),
        )

        logger.info(
            "Standardized file: %s",
            standardized_file,
        )

        # 11. Marquer le batch
        # comme terminé avec succès
        batch.status = "SUCCESS"

        save_batch(batch)

        logger.info(
            "Batch status: SUCCESS"
        )

        # Retourner l'identifiant du batch
        return batch.batch_id

    except Exception:

        # 12. Si n'importe quelle étape échoue,
        # enregistrer FAILED
        batch.status = "FAILED"

        save_batch(batch)

        logger.exception(
            "Batch failed: %s",
            batch.batch_id,
        )

        # On laisse l'erreur remonter
        # pour faciliter le debug
        raise


def main():

    source_file = Path(
        r"C:\Users\hp\Desktop\stage 2A-Quality Intelligence Platform\quality-intelligence-platform\data\raw\QHC_ISO9001_test_Audits & consolidation FY27 (1).xlsx"
    )

    run_ingestion(
        source_file=source_file,
        campaign=CURRENT_CAMPAIGN,
    )


if __name__ == "__main__":
    main()