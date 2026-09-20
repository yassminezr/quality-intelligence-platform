from pathlib import Path

import pandas as pd


STATUS_MAPPING = {
    "réalisé": "audite",
    "realise": "audite",
    "réalisée": "audite",
    "realisee": "audite",
    "audité": "audite",
    "audite": "audite",

    "en cours": "en_cours",

    "planifié": "non_audite",
    "planifie": "non_audite",

    "non démarré": "non_audite",
    "non demarre": "non_audite",
    "non audité": "non_audite",
    "non audite": "non_audite",
    "non auditée": "non_audite",
    "non auditee": "non_audite",
}


def normalize_text(value):
    if pd.isna(value):
        return None

    return str(value).strip()


def normalize_status(value):
    value = normalize_text(value)

    if value is None:
        return None

    return STATUS_MAPPING.get(value.lower())


def find_dashboard_header(df: pd.DataFrame) -> int:
    """
    Recherche la ligne d'en-tête contenant les colonnes
    Compte et Statut.
    """

    for index, row in df.head(40).iterrows():
        values = {
            str(value).strip().lower()
            for value in row.tolist()
            if pd.notna(value)
        }

        has_account = any(
            value in {"compte", "account"}
            for value in values
        )

        has_status = any(
            value in {"statut", "status"}
            for value in values
        )

        if has_account and has_status:
            return index

    raise ValueError(
        "Impossible de trouver les colonnes Compte et Statut "
        "dans la feuille DASHBOARD AUDITS."
    )


def extract_audit_statuses(excel_file: Path) -> pd.DataFrame:
    raw = pd.read_excel(
        excel_file,
        sheet_name="DASHBOARD AUDITS",
        header=None,
    )

    header_row = find_dashboard_header(raw)

    df = pd.read_excel(
        excel_file,
        sheet_name="DASHBOARD AUDITS",
        header=header_row,
    )

    account_column = next(
        column
        for column in df.columns
        if str(column).strip().lower()
        in {"compte", "account"}
    )

    status_column = next(
        column
        for column in df.columns
        if str(column).strip().lower()
        in {"statut", "status"}
    )

    result = pd.DataFrame()

    result["account_name"] = (
        df[account_column]
        .apply(normalize_text)
    )

    result["source_status"] = (
        df[status_column]
        .apply(normalize_text)
    )

    result["validated_status"] = (
        result["source_status"]
        .apply(normalize_status)
    )

    result = result[
        result["account_name"].notna()
    ].copy()

    unknown = result[
        result["source_status"].notna()
        & result["validated_status"].isna()
    ]

    if not unknown.empty:
        unknown_values = sorted(
            unknown["source_status"]
            .astype(str)
            .unique()
        )

        raise ValueError(
            "Statuts inconnus dans DASHBOARD AUDITS : "
            + ", ".join(unknown_values)
        )

    result = result[
        result["validated_status"].notna()
    ].copy()

    return result[
        [
            "account_name",
            "source_status",
            "validated_status",
        ]
    ]