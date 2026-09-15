from __future__ import annotations

import argparse
import re

import pandas as pd

from src.common.database import (
    get_postgres_connection,
)

from src.modeling.history_utils import (
    save_action_status_version,
    save_evaluation_version,
    values_changed,
)


VALID_FINDING_CATEGORIES = {
    "NC Mineure",
    "NC Majeure",
    "Bonne Pratique",
    "OFI",
    "Observation",
    "NA",
}


def normalize_text(value):
    """
    Retourne un texte nettoyé
    ou None si la valeur est vide.
    """

    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


def is_valid_iso_clause(value) -> bool:
    """
    Vérifie qu'une valeur correspond
    réellement à une clause ISO.

    Exemples valides :
    4.1
    7.1.1
    8.5.6
    10.2

    Exemples exclus :
    Contexte
    Leadership
    Support
    Libellé
    """

    value = normalize_text(value)

    if value is None:
        return False

    return bool(
        re.fullmatch(
            r"(?:[4-9]|10)(?:\.\d+)+",
            value,
        )
    )


def is_evaluated_row(row) -> bool:
    """
    Une ligne est considérée comme évaluée
    si au moins un résultat d'audit existe.
    """

    fields = [
        row.score_maturite,
        row.niveau_maturite,
        row.constat_auditeur,
        row.categorie_finding,
    ]

    return any(
        normalize_text(value) is not None
        for value in fields
    )


def normalize_score(value):
    """
    Convertit le score en entier uniquement
    si la valeur est comprise entre 1 et 5.
    """

    if pd.isna(value):
        return None

    try:
        numeric_value = float(value)

    except (TypeError, ValueError):
        return None

    if not numeric_value.is_integer():
        return None

    score = int(numeric_value)

    if 1 <= score <= 5:
        return score

    return None


def normalize_date(value):
    """
    Convertit une valeur en date Python.

    Une date invalide retourne None.
    """

    value = normalize_text(value)

    if value is None:
        return None

    parsed = pd.to_datetime(
        value,
        errors="coerce",
    )

    if pd.isna(parsed):
        return None

    return parsed.date()


def load_evaluation_core(
    batch_id: str,
) -> dict[str, int]:
    """
    Alimente et met à jour :

    - core.evaluation
    - core.finding
    - core.corrective_action

    Historise également :
    - les modifications d'évaluation
    - les changements de statut des actions
    """

    connection = get_postgres_connection()

    evaluation_count = 0
    finding_count = 0
    action_count = 0

    skipped_unevaluated = 0
    skipped_structural = 0

    evaluation_changes = 0
    action_changes = 0
    action_status_changes = 0

    try:

        # ---------------------------------
        # 1. Lire le staging du batch
        # ---------------------------------

        dataframe = pd.read_sql_query(
            """
            SELECT
                source_sheet,
                clause_iso,
                libelle_terrain,
                score_maturite,
                niveau_maturite,
                constat_auditeur,
                categorie_finding,
                action_corrective,
                responsable_action,
                date_debut,
                date_cloture,
                statut_action,
                evidence,
                commentaires
            FROM staging.standardized_audits
            WHERE batch_id = %s;
            """,
            connection,
            params=(batch_id,),
        )

        if dataframe.empty:
            raise ValueError(
                f"No staging data found "
                f"for batch {batch_id}"
            )

        with connection.cursor() as cursor:

            # ---------------------------------
            # 2. Récupérer la campagne
            # ---------------------------------

            cursor.execute(
                """
                SELECT campaign
                FROM metadata.ingestion_batch
                WHERE batch_id = %s;
                """,
                (batch_id,),
            )

            result = cursor.fetchone()

            if result is None:
                raise ValueError(
                    f"Batch metadata not found: "
                    f"{batch_id}"
                )

            campaign_name = result[0]

            cursor.execute(
                """
                SELECT campaign_id
                FROM core.campaign
                WHERE campaign_name = %s;
                """,
                (campaign_name,),
            )

            result = cursor.fetchone()

            if result is None:
                raise ValueError(
                    f"Campaign not found in core: "
                    f"{campaign_name}"
                )

            campaign_id = result[0]

            # ---------------------------------
            # 3. Parcourir les lignes staging
            # ---------------------------------

            for row in dataframe.itertuples(
                index=False
            ):

                clause_iso = normalize_text(
                    row.clause_iso
                )

                # -----------------------------
                # Ignorer lignes structurelles
                # -----------------------------

                if not is_valid_iso_clause(
                    clause_iso
                ):
                    skipped_structural += 1
                    continue

                # -----------------------------
                # Ignorer lignes non évaluées
                # -----------------------------

                if not is_evaluated_row(row):
                    skipped_unevaluated += 1
                    continue

                account_name = normalize_text(
                    row.source_sheet
                )

                libelle_terrain = normalize_text(
                    row.libelle_terrain
                )

                if (
                    account_name is None
                    or libelle_terrain is None
                ):
                    continue

                # -----------------------------
                # Trouver audit
                # -----------------------------

                cursor.execute(
                    """
                    SELECT au.audit_id
                    FROM core.audit au

                    JOIN core.account acc
                        ON acc.account_id =
                           au.account_id

                    WHERE
                        acc.account_name = %s
                        AND au.campaign_id = %s;
                    """,
                    (
                        account_name,
                        campaign_id,
                    ),
                )

                audit_result = cursor.fetchone()

                if audit_result is None:
                    raise ValueError(
                        f"Audit not found for "
                        f"{account_name}"
                    )

                audit_id = audit_result[0]

                # -----------------------------
                # Trouver contrôle ISO
                # -----------------------------

                cursor.execute(
                    """
                    SELECT ic.control_id

                    FROM core.iso_control ic

                    JOIN core.iso_clause c
                        ON c.clause_id =
                           ic.clause_id

                    WHERE
                        c.clause_iso = %s
                        AND ic.libelle_terrain = %s;
                    """,
                    (
                        clause_iso,
                        libelle_terrain,
                    ),
                )

                control_result = (
                    cursor.fetchone()
                )

                if control_result is None:
                    raise ValueError(
                        "ISO control not found for "
                        f"{clause_iso} / "
                        f"{libelle_terrain}"
                    )

                control_id = control_result[0]

                # -----------------------------
                # Préparer valeurs Evaluation
                # -----------------------------

                score = normalize_score(
                    row.score_maturite
                )

                niveau = normalize_text(
                    row.niveau_maturite
                )

                constat = normalize_text(
                    row.constat_auditeur
                )

                evidence = normalize_text(
                    row.evidence
                )

                commentaires = normalize_text(
                    row.commentaires
                )

                new_evaluation_values = (
                    score,
                    niveau,
                    constat,
                    evidence,
                    commentaires,
                )

                # =================================
                # EVALUATION
                # =================================

                cursor.execute(
                    """
                    SELECT
                        evaluation_id,
                        score_maturite,
                        niveau_maturite,
                        constat_auditeur,
                        evidence,
                        commentaires

                    FROM core.evaluation

                    WHERE
                        audit_id = %s
                        AND control_id = %s;
                    """,
                    (
                        audit_id,
                        control_id,
                    ),
                )

                existing_evaluation = (
                    cursor.fetchone()
                )

                # -----------------------------
                # Nouvelle évaluation
                # -----------------------------

                if existing_evaluation is None:

                    cursor.execute(
                        """
                        INSERT INTO core.evaluation (
                            audit_id,
                            control_id,
                            score_maturite,
                            niveau_maturite,
                            constat_auditeur,
                            evidence,
                            commentaires
                        )
                        VALUES (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s
                        )
                        RETURNING evaluation_id;
                        """,
                        (
                            audit_id,
                            control_id,
                            score,
                            niveau,
                            constat,
                            evidence,
                            commentaires,
                        ),
                    )

                    evaluation_id = (
                        cursor.fetchone()[0]
                    )

                    # Historique initial
                    save_evaluation_version(
                        cursor=cursor,
                        evaluation_id=(
                            evaluation_id
                        ),
                        batch_id=batch_id,
                        score_maturite=score,
                        niveau_maturite=niveau,
                        constat_auditeur=constat,
                    )

                # -----------------------------
                # Evaluation déjà existante
                # -----------------------------

                else:

                    evaluation_id = (
                        existing_evaluation[0]
                    )

                    current_evaluation_values = (
                        existing_evaluation[1],
                        existing_evaluation[2],
                        existing_evaluation[3],
                        existing_evaluation[4],
                        existing_evaluation[5],
                    )

                    if values_changed(
                        current_evaluation_values,
                        new_evaluation_values,
                    ):

                        cursor.execute(
                            """
                            UPDATE core.evaluation

                            SET
                                score_maturite = %s,
                                niveau_maturite = %s,
                                constat_auditeur = %s,
                                evidence = %s,
                                commentaires = %s,
                                updated_at = NOW()

                            WHERE
                                evaluation_id = %s;
                            """,
                            (
                                score,
                                niveau,
                                constat,
                                evidence,
                                commentaires,
                                evaluation_id,
                            ),
                        )

                        save_evaluation_version(
                            cursor=cursor,
                            evaluation_id=(
                                evaluation_id
                            ),
                            batch_id=batch_id,
                            score_maturite=score,
                            niveau_maturite=niveau,
                            constat_auditeur=constat,
                        )

                        evaluation_changes += 1

                evaluation_count += 1

                # =================================
                # FINDING
                # =================================

                finding_category = (
                    normalize_text(
                        row.categorie_finding
                    )
                )

                # Pas de finding exploitable
                if (
                    finding_category
                    not in VALID_FINDING_CATEGORIES
                ):
                    continue

                cursor.execute(
                    """
                    INSERT INTO core.finding (
                        evaluation_id,
                        categorie_finding
                    )
                    VALUES (
                        %s,
                        %s
                    )

                    ON CONFLICT (
                        evaluation_id
                    )

                    DO UPDATE SET
                        categorie_finding =
                            EXCLUDED.categorie_finding

                    RETURNING finding_id;
                    """,
                    (
                        evaluation_id,
                        finding_category,
                    ),
                )

                finding_id = (
                    cursor.fetchone()[0]
                )

                finding_count += 1

                # =================================
                # CORRECTIVE ACTION
                # =================================

                action_text = normalize_text(
                    row.action_corrective
                )

                # Pas d'action si :
                # - action vide
                # - finding = NA
                if (
                    action_text is None
                    or finding_category == "NA"
                ):
                    continue

                responsable = normalize_text(
                    row.responsable_action
                )

                date_debut = normalize_date(
                    row.date_debut
                )

                date_cloture = normalize_date(
                    row.date_cloture
                )

                statut = normalize_text(
                    row.statut_action
                )

                # Protection Core :
                # date_cloture antérieure
                # à date_debut → non propagée.
                if (
                    date_debut is not None
                    and date_cloture is not None
                    and date_cloture
                    < date_debut
                ):
                    date_cloture = None

                # -----------------------------
                # Chercher action existante
                # -----------------------------

                cursor.execute(
                    """
                    SELECT
                        action_id,
                        action_text,
                        responsable,
                        date_debut,
                        date_cloture,
                        statut

                    FROM core.corrective_action

                    WHERE finding_id = %s;
                    """,
                    (finding_id,),
                )

                existing_action = (
                    cursor.fetchone()
                )

                # -----------------------------
                # Nouvelle action
                # -----------------------------

                if existing_action is None:

                    cursor.execute(
                        """
                        INSERT INTO core.corrective_action (
                            finding_id,
                            action_text,
                            responsable,
                            date_debut,
                            date_cloture,
                            statut
                        )
                        VALUES (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s
                        )
                        RETURNING action_id;
                        """,
                        (
                            finding_id,
                            action_text,
                            responsable,
                            date_debut,
                            date_cloture,
                            statut,
                        ),
                    )

                    action_id = (
                        cursor.fetchone()[0]
                    )

                    # Historique initial du statut
                    save_action_status_version(
                        cursor=cursor,
                        action_id=action_id,
                        batch_id=batch_id,
                        status=statut,
                    )

                # -----------------------------
                # Action déjà existante
                # -----------------------------

                else:

                    action_id = (
                        existing_action[0]
                    )

                    previous_status = (
                        existing_action[5]
                    )

                    current_action_values = (
                        existing_action[1],
                        existing_action[2],
                        existing_action[3],
                        existing_action[4],
                        existing_action[5],
                    )

                    new_action_values = (
                        action_text,
                        responsable,
                        date_debut,
                        date_cloture,
                        statut,
                    )

                    # Mise à jour seulement si
                    # un changement réel existe
                    if values_changed(
                        current_action_values,
                        new_action_values,
                    ):

                        cursor.execute(
                            """
                            UPDATE
                                core.corrective_action

                            SET
                                action_text = %s,
                                responsable = %s,
                                date_debut = %s,
                                date_cloture = %s,
                                statut = %s,
                                updated_at = NOW()

                            WHERE
                                action_id = %s;
                            """,
                            (
                                action_text,
                                responsable,
                                date_debut,
                                date_cloture,
                                statut,
                                action_id,
                            ),
                        )

                        action_changes += 1

                    # Historique seulement
                    # si statut réellement changé
                    if previous_status != statut:

                        save_action_status_version(
                            cursor=cursor,
                            action_id=action_id,
                            batch_id=batch_id,
                            status=statut,
                        )

                        action_status_changes += 1

                action_count += 1

        # ---------------------------------
        # Commit transaction
        # ---------------------------------

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return {
        "evaluations": evaluation_count,
        "findings": finding_count,
        "actions": action_count,
        "skipped_unevaluated": (
            skipped_unevaluated
        ),
        "skipped_structural": (
            skipped_structural
        ),
        "evaluation_changes": (
            evaluation_changes
        ),
        "action_changes": (
            action_changes
        ),
        "action_status_changes": (
            action_status_changes
        ),
    }


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Load evaluations, findings, "
            "corrective actions and history "
            "into PostgreSQL core."
        )
    )

    parser.add_argument(
        "--batch-id",
        required=True,
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    result = load_evaluation_core(
        batch_id=args.batch_id
    )

    print(
        "Evaluation core loading completed."
    )

    print(
        "Evaluations:",
        result["evaluations"],
    )

    print(
        "Findings:",
        result["findings"],
    )

    print(
        "Corrective actions:",
        result["actions"],
    )

    print(
        "Skipped unevaluated rows:",
        result[
            "skipped_unevaluated"
        ],
    )

    print(
        "Skipped structural rows:",
        result[
            "skipped_structural"
        ],
    )

    print(
        "Evaluation changes:",
        result[
            "evaluation_changes"
        ],
    )

    print(
        "Action changes:",
        result[
            "action_changes"
        ],
    )

    print(
        "Action status changes:",
        result[
            "action_status_changes"
        ],
    )


if __name__ == "__main__":
    main()