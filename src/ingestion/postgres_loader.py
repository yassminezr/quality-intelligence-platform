from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.common.config import RAW_DIR
from src.common.database import (
    get_postgres_connection,
)


BATCH_METADATA_FILE = (
    RAW_DIR
    / "_metadata"
    / "ingestion_batches.jsonl"
)


STAGING_COLUMNS = [
    "source_file",
    "source_sheet",
    "source_row_number",
    "clause_iso",
    "intitule_iso",
    "libelle_terrain",
    "controle_attendu",
    "categorie_scope",
    "reference_edge",
    "preuves_attendues",
    "constat_auditeur",
    "categorie_finding",
    "niveau_maturite",
    "score_maturite",
    "action_corrective",
    "responsable_action",
    "date_debut",
    "date_cloture",
    "statut_action",
    "age_jours",
    "indicateur_age",
    "evidence",
    "commentaires",
]


def find_batch_metadata(
    batch_id: str,
) -> dict[str, Any]:
    """
    Recherche dans le prototype JSONL
    les métadonnées du batch demandé.

    Si plusieurs événements existent pour
    le même batch, le dernier est retenu.
    """

    if not BATCH_METADATA_FILE.exists():
        raise FileNotFoundError(
            f"Metadata file not found: "
            f"{BATCH_METADATA_FILE}"
        )

    matching_batch = None

    with BATCH_METADATA_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)

            if (
                record.get("batch_id")
                == batch_id
            ):
                matching_batch = record

    if matching_batch is None:
        raise ValueError(
            f"Batch not found: {batch_id}"
        )

    return matching_batch


def normalize_dataframe(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prépare le DataFrame avant insertion.

    Les colonnes staging manquantes sont
    ajoutées avec une valeur NULL.
    """

    df = dataframe.copy()

    for column in STAGING_COLUMNS:
        if column not in df.columns:
            df[column] = None

    df = df[STAGING_COLUMNS]

    # NaN / NaT → None pour PostgreSQL
    df = df.astype(object).where(
        pd.notna(df),
        None,
    )

    return df


def insert_batch_metadata(
    cursor,
    batch: dict[str, Any],
) -> None:
    """
    Enregistre le batch dans PostgreSQL.

    ON CONFLICT permet de rejouer le loader
    sans recréer le même batch.
    """

    cursor.execute(
        """
        INSERT INTO metadata.ingestion_batch (
            batch_id,
            campaign,
            source_file,
            file_hash,
            ingestion_timestamp,
            status
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ON CONFLICT (batch_id)
        DO UPDATE SET
            campaign = EXCLUDED.campaign,
            source_file = EXCLUDED.source_file,
            file_hash = EXCLUDED.file_hash,
            ingestion_timestamp = EXCLUDED.ingestion_timestamp,
            status = EXCLUDED.status;
        """,
        (
            batch["batch_id"],
            batch["campaign"],
            batch["source_file"],
            batch["file_hash"],
            batch["ingestion_timestamp"],
            batch["status"],
        ),
    )


def load_standardized_batch(
    csv_path: Path,
    batch_id: str,
) -> int:
    """
    Charge un fichier standardized_audits.csv
    dans PostgreSQL staging.

    Retourne le nombre de lignes chargées.
    """

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV not found: {csv_path}"
        )

    batch = find_batch_metadata(
        batch_id
    )

    dataframe = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
    )

    dataframe = normalize_dataframe(
        dataframe
    )

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            # 1. Enregistrer les métadonnées
            insert_batch_metadata(
                cursor=cursor,
                batch=batch,
            )

            # 2. Idempotence :
            # si le batch avait déjà été chargé,
            # supprimer ses anciennes lignes staging.
            cursor.execute(
                """
                DELETE FROM staging.standardized_audits
                WHERE batch_id = %s;
                """,
                (batch_id,),
            )

            insert_sql = """
                INSERT INTO staging.standardized_audits (
                    batch_id,
                    source_file,
                    source_sheet,
                    source_row_number,
                    clause_iso,
                    intitule_iso,
                    libelle_terrain,
                    controle_attendu,
                    categorie_scope,
                    reference_edge,
                    preuves_attendues,
                    constat_auditeur,
                    categorie_finding,
                    niveau_maturite,
                    score_maturite,
                    action_corrective,
                    responsable_action,
                    date_debut,
                    date_cloture,
                    statut_action,
                    age_jours,
                    indicateur_age,
                    evidence,
                    commentaires
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                );
            """

            for row in dataframe.itertuples(
                index=False,
                name=None,
            ):
                cursor.execute(
                    insert_sql,
                    (
                        batch_id,
                        *row,
                    ),
                )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return len(dataframe)