from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.quality.dq_models import (
    DQReport,
)


RULE_DESCRIPTIONS = {
    "DQ_SCHEMA_001": {
        "rule_name": "Colonne obligatoire absente",
        "business_description": (
            "Une colonne indispensable au traitement "
            "est absente du fichier."
        ),
        "recommended_action": (
            "Vérifier la structure du fichier source."
        ),
    },
    "DQ_DOMAIN_001": {
        "rule_name": "Score de maturité invalide",
        "business_description": (
            "Le score de maturité renseigné "
            "n'est pas compris entre 1 et 5."
        ),
        "recommended_action": (
            "Corriger le score dans la source."
        ),
    },
    "DQ_DOMAIN_002": {
        "rule_name": "Catégorie de finding invalide",
        "business_description": (
            "La catégorie de finding ne fait pas partie "
            "du référentiel métier autorisé."
        ),
        "recommended_action": (
            "Vérifier et corriger la catégorie de finding."
        ),
    },
    "DQ_COMPLETENESS_001": {
        "rule_name": "Finding manquant après évaluation",
        "business_description": (
            "La ligne semble avoir été évaluée, "
            "mais aucune catégorie de finding "
            "n'a été renseignée."
        ),
        "recommended_action": (
            "Compléter la catégorie de finding : "
            "NC Mineure, NC Majeure, Bonne Pratique, "
            "OFI, Observation ou NA."
        ),
    },
    "DQ_CONSISTENCY_001": {
        "rule_name": "Action présente avec finding NA",
        "business_description": (
            "Une action corrective est renseignée "
            "alors que le finding est NA."
        ),
        "recommended_action": (
            "Vérifier si l'action est réellement "
            "une action corrective."
        ),
    },
    "DQ_CONSISTENCY_002": {
        "rule_name": "Action sans finding valide",
        "business_description": (
            "Une action corrective est renseignée, "
            "mais la catégorie de finding est absente "
            "ou égale à NA."
        ),
        "recommended_action": (
            "Vérifier la catégorie de finding et "
            "la nature de l'action saisie."
        ),
    },
    "DQ_CONSISTENCY_003": {
        "rule_name": "Action clôturée sans date",
        "business_description": (
            "Une action est déclarée clôturée, "
            "mais aucune date de clôture n'est renseignée."
        ),
        "recommended_action": (
            "Renseigner ou vérifier la date de clôture."
        ),
    },
    "DQ_DATE_001": {
        "rule_name": "Date invalide",
        "business_description": (
            "Une date renseignée ne peut pas être "
            "interprétée correctement."
        ),
        "recommended_action": (
            "Corriger le format ou la valeur de la date."
        ),
    },
    "DQ_DATE_002": {
        "rule_name": "Chronologie des dates incohérente",
        "business_description": (
            "La date de clôture est antérieure "
            "à la date de début."
        ),
        "recommended_action": (
            "Vérifier les deux dates."
        ),
    },
}


def report_to_dataframe(
    report: DQReport,
) -> pd.DataFrame:
    """
    Convertit les anomalies Data Quality
    en DataFrame enrichi pour le reporting métier.
    """

    rows = []

    for issue in report.issues:
        rule_info = RULE_DESCRIPTIONS.get(
            issue.rule_id,
            {
                "rule_name": issue.rule_id,
                "business_description": issue.message,
                "recommended_action": "À analyser.",
            },
        )

        rows.append(
            {
                "rule_id": issue.rule_id,
                "rule_name": rule_info["rule_name"],
                "severity": issue.severity.value,
                "account": issue.source_sheet,
                "source_row_number": (
                    issue.source_row_number
                ),
                "technical_message": issue.message,
                "business_description": (
                    rule_info[
                        "business_description"
                    ]
                ),
                "recommended_action": (
                    rule_info[
                        "recommended_action"
                    ]
                ),
                "source_file": issue.source_file,
            }
        )

    return pd.DataFrame(rows)


def save_business_reports(
    report: DQReport,
    output_dir: Path,
) -> None:
    """
    Génère les synthèses Data Quality
    destinées à l'équipe Qualité.
    """

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    issues_df = report_to_dataframe(
        report
    )

    if issues_df.empty:
        by_rule = pd.DataFrame(
            columns=[
                "rule_id",
                "rule_name",
                "severity",
                "issue_count",
            ]
        )

        by_account = pd.DataFrame(
            columns=[
                "account",
                "issue_count",
            ]
        )

    else:
        by_rule = (
            issues_df
            .groupby(
                [
                    "rule_id",
                    "rule_name",
                    "severity",
                ],
                dropna=False,
            )
            .size()
            .reset_index(
                name="issue_count"
            )
            .sort_values(
                "issue_count",
                ascending=False,
            )
        )

        by_account = (
            issues_df
            .groupby(
                "account",
                dropna=False,
            )
            .size()
            .reset_index(
                name="issue_count"
            )
            .sort_values(
                "issue_count",
                ascending=False,
            )
        )

    by_rule.to_csv(
        output_dir
        / "dq_summary_by_rule.csv",
        index=False,
        encoding="utf-8-sig",
    )

    by_account.to_csv(
        output_dir
        / "dq_summary_by_account.csv",
        index=False,
        encoding="utf-8-sig",
    )

    issues_df.to_csv(
        output_dir
        / "dq_issues_business.csv",
        index=False,
        encoding="utf-8-sig",
    )