import pandas as pd
import plotly.express as px
import streamlit as st

from data.loaders import (
    load_audit_overview,
    load_account_clause_detail,
    load_findings,
    load_corrective_actions,
)

from styles.theme import (
    apply_global_theme,
    render_sidebar,
    render_header,
    kpi_card,
    MIDNIGHT_BLUE,
    ROYAL,
    SKY,
    RED,
    GOLD,
    PEACH,
    CHARCOAL,
    SOFT_BLUE,
    SOFT_SKY,
    SOFT_GOLD,
    SOFT_RED,
    SOFT_GRAY,
)


# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Détail Compte | QIP",
    page_icon="🔎",
    layout="wide",
)

apply_global_theme()
render_sidebar()

render_header(
    "Détail Compte",
    "Résultat QHC détaillé par compte",
)


# =====================================================
# HELPERS
# =====================================================

STATUS_LABELS = {
    "audite": "Audité",
    "en_cours": "En cours",
    "non_audite": "Non démarré",
}


def badge_from_score(score):

    if pd.isna(score):
        return "—"

    if score >= 4.5:
        return "Très Performant"

    if score >= 3.5:
        return "Performant"

    if score >= 2.5:
        return "À surveiller"

    if score >= 1.5:
        return "À Risque"

    return "Critique"


def chapter_from_clause(clause):

    if pd.isna(clause):
        return None

    value = str(clause).strip()

    if not value:
        return None

    return value.split(".")[0]


CHAPTER_LABELS = {
    "4": "Contexte",
    "5": "Leadership",
    "6": "Planification",
    "7": "Support",
    "8": "Réalisation",
    "9": "Performance",
    "10": "Amélioration",
}


# =====================================================
# DATA
# =====================================================

audit_df = load_audit_overview()
detail_df = load_account_clause_detail()
findings_df = load_findings()
actions_df = load_corrective_actions()


# =====================================================
# FILTRE COMPTE
# =====================================================

accounts = sorted(
    audit_df["account_name"]
    .dropna()
    .unique()
    .tolist()
)


selected_account = st.selectbox(
    "Compte",
    accounts,
)


# =====================================================
# FILTER DATA
# =====================================================

account_audit = audit_df[
    audit_df["account_name"]
    == selected_account
].copy()


account_detail = detail_df[
    detail_df["account_name"]
    == selected_account
].copy()


account_findings = findings_df[
    findings_df["account_name"]
    == selected_account
].copy()


account_actions = actions_df[
    actions_df["account_name"]
    == selected_account
].copy()


if account_audit.empty:
    st.warning(
        "Aucune donnée disponible pour ce compte."
    )
    st.stop()


audit_row = account_audit.iloc[0]


# =====================================================
# ACCOUNT BANNER
# =====================================================

official_status = STATUS_LABELS.get(
    audit_row["official_audit_status"],
    audit_row["official_audit_status"],
)


st.info(
    f"Compte : {selected_account}  |  "
    f"Statut officiel : {official_status}"
)


# =====================================================
# KPI
# =====================================================

score = audit_row[
    "avg_maturity_score"
]

badge = audit_row[
    "account_badge"
]

completion = audit_row[
    "completion_rate"
]


nc_major = len(
    account_findings[
        account_findings[
            "categorie_finding"
        ]
        == "NC Majeure"
    ]
)


nc_minor = len(
    account_findings[
        account_findings[
            "categorie_finding"
        ]
        == "NC Mineure"
    ]
)


observations = len(
    account_findings[
        account_findings[
            "categorie_finding"
        ]
        == "Observation"
    ]
)


ofi = len(
    account_findings[
        account_findings[
            "categorie_finding"
        ]
        == "OFI"
    ]
)


bp = len(
    account_findings[
        account_findings[
            "categorie_finding"
        ]
        == "Bonne Pratique"
    ]
)


total_findings = len(
    account_findings[
        account_findings[
            "is_counted_in_total_findings"
        ]
        == True
    ]
)


open_actions = len(
    account_actions[
        account_actions["is_open"]
        == True
    ]
)


age_mean = (
    account_actions[
        "age_jours"
    ]
    .dropna()
    .mean()
)


# =====================================================
# KPI — LIGNE 1
# =====================================================

st.markdown(
    '<div class="section-title">'
    'Indicateurs clés'
    '</div>',
    unsafe_allow_html=True,
)


k1, k2, k3, k4 = st.columns(4)


with k1:

    score_display = (
        f"{score:.2f} / 5"
        if pd.notna(score)
        else "—"
    )

    kpi_card(
        "Score maturité",
        score_display,
        ROYAL,
        SOFT_SKY,
    )


with k2:

    kpi_card(
        "Badge",
        badge if pd.notna(badge) else "—",
        GOLD,
        SOFT_GOLD,
    )


with k3:

    kpi_card(
        "% Avancement",
        f"{completion:.1f} %",
        ROYAL,
        SKY,
    )


with k4:

    kpi_card(
        "Total Findings",
        total_findings,
        GOLD,
        PEACH,
    )


# =====================================================
# KPI — LIGNE 2
# =====================================================

st.markdown(
    "<br>",
    unsafe_allow_html=True,
)


k5, k6, k7, k8, k9 = st.columns(5)


with k5:

    kpi_card(
        "NC Majeures",
        nc_major,
        RED,
        SOFT_RED,
    )


with k6:

    kpi_card(
        "NC Mineures",
        nc_minor,
        PEACH,
        SOFT_GOLD,
    )


with k7:

    kpi_card(
        "Observations",
        observations,
        ROYAL,
        SOFT_SKY,
    )


with k8:

    kpi_card(
        "OFI",
        ofi,
        GOLD,
        SOFT_GOLD,
    )


with k9:

    kpi_card(
        "Bonnes Pratiques",
        bp,
        ROYAL,
        SKY,
    )


# =====================================================
# KPI — ACTIONS
# =====================================================

st.markdown(
    "<br>",
    unsafe_allow_html=True,
)


a1, a2 = st.columns(2)


with a1:

    kpi_card(
        "Actions ouvertes",
        open_actions,
        RED if open_actions > 0 else ROYAL,
        SOFT_RED if open_actions > 0 else SOFT_BLUE,
    )


with a2:

    age_display = (
        f"{age_mean:.0f} jours"
        if pd.notna(age_mean)
        else "—"
    )

    kpi_card(
        "Ancienneté moyenne",
        age_display,
        GOLD,
        SOFT_GOLD,
    )


# =====================================================
# MATURITE PAR CHAPITRE
# =====================================================

st.markdown(
    '<div class="section-title">'
    'Maturité par chapitre'
    '</div>',
    unsafe_allow_html=True,
)


chapter_df = account_detail.copy()


chapter_df[
    "Chapitre"
] = (
    chapter_df[
        "clause_iso"
    ]
    .apply(
        chapter_from_clause
    )
)


chapter_df = chapter_df[
    chapter_df["Chapitre"].isin(
        CHAPTER_LABELS.keys()
    )
].copy()


chapter_summary = (
    chapter_df
    .groupby(
        "Chapitre",
        as_index=False,
    )
    .agg(
        Nb_Clauses=(
            "control_id",
            "count",
        ),

        Score_Moyen=(
            "score_maturite",
            "mean",
        ),
    )
)


chapter_summary[
    "Chapitre_num"
] = (
    chapter_summary[
        "Chapitre"
    ]
    .astype(int)
)


chapter_summary = chapter_summary.sort_values(
    "Chapitre_num"
)


chapter_summary[
    "Libellé"
] = (
    chapter_summary[
        "Chapitre"
    ]
    .map(
        CHAPTER_LABELS
    )
)


chapter_summary[
    "Badge"
] = (
    chapter_summary[
        "Score_Moyen"
    ]
    .apply(
        badge_from_score
    )
)


chapter_summary[
    "Chapitre"
] = (
    "Ch"
    + chapter_summary[
        "Chapitre"
    ]
)


chapter_display = chapter_summary[
    [
        "Chapitre",
        "Libellé",
        "Nb_Clauses",
        "Score_Moyen",
        "Badge",
    ]
].copy()


chapter_display = chapter_display.rename(
    columns={
        "Nb_Clauses": "Nb Clauses",
        "Score_Moyen": "Score Moyen",
    }
)


# =====================================================
# STYLE TABLE CHAPTER
# =====================================================

def style_badge(value):

    if value == "Très Performant":
        return (
            f"background-color:{SKY};"
            f"color:{ROYAL};"
            "font-weight:800;"
        )

    if value == "Performant":
        return (
            "background-color:#DCEEFF;"
            f"color:{ROYAL};"
            "font-weight:800;"
        )

    if value == "À surveiller":
        return (
            f"background-color:{GOLD};"
            f"color:{MIDNIGHT_BLUE};"
            "font-weight:800;"
        )

    if value == "À Risque":
        return (
            f"background-color:{PEACH};"
            f"color:{CHARCOAL};"
            "font-weight:800;"
        )

    if value == "Critique":
        return (
            f"background-color:{RED};"
            "color:white;"
            "font-weight:850;"
        )

    return (
        "background-color:#F0F1F3;"
        "color:#888888;"
    )


styled_chapter = (
    chapter_display.style

    .format(
        {
            "Score Moyen": lambda value:
                "WIP"
                if pd.isna(value)
                else f"{value:.2f}",
        }
    )

    .set_table_styles(
        [
            {
                "selector": "thead th",
                "props": [
                    (
                        "background-color",
                        MIDNIGHT_BLUE,
                    ),
                    (
                        "color",
                        "white",
                    ),
                    (
                        "font-weight",
                        "800",
                    ),
                ],
            }
        ]
    )

    .map(
        style_badge,
        subset=["Badge"],
    )
)


left, right = st.columns(
    [1.7, 1]
)


with left:

    st.dataframe(
        styled_chapter,
        use_container_width=True,
        hide_index=True,
    )


# =====================================================
# STATUT ACTIONS
# =====================================================

with right:

    if not account_actions.empty:

        action_status = (
            account_actions[
                "statut"
            ]
            .fillna(
                "Non renseigné"
            )
            .value_counts()
            .rename_axis(
                "Statut"
            )
            .reset_index(
                name="Nombre"
            )
        )


        fig_actions = px.pie(
            action_status,
            names="Statut",
            values="Nombre",
            hole=0.62,
            color_discrete_sequence=[
                ROYAL,
                GOLD,
                RED,
                SKY,
            ],
        )


        fig_actions.update_traces(
            textinfo="value+percent",
            textposition="inside",
        )


        fig_actions.update_layout(
            title="Statut des actions",
            legend_title_text="",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(
                color=MIDNIGHT_BLUE
            ),
        )


        st.plotly_chart(
            fig_actions,
            use_container_width=True,
        )

    else:

        st.info(
            "Aucune action corrective "
            "pour ce compte."
        )


# =====================================================
# DETAIL DES CLAUSES
# =====================================================

st.markdown(
    '<div class="section-title">'
    'Détail des clauses'
    '</div>',
    unsafe_allow_html=True,
)


detail_table = account_detail[
    [
        "clause_iso",
        "libelle_terrain",
        "controle_attendu",
        "score_maturite",
        "niveau_maturite",
        "constat_auditeur",
        "categorie_finding",
        "action_text",
        "responsable",
        "action_status",
        "age_jours",
        "indicateur_age",
    ]
].copy()


detail_table = detail_table.rename(
    columns={
        "clause_iso": "Clause ISO",
        "libelle_terrain": "Libellé Terrain",
        "controle_attendu": "Contrôle attendu",
        "score_maturite": "Score",
        "niveau_maturite": "Niveau maturité",
        "constat_auditeur": "Constat",
        "categorie_finding": "Finding",
        "action_text": "Action corrective",
        "responsable": "Responsable",
        "action_status": "Statut action",
        "age_jours": "Âge",
        "indicateur_age": "Indicateur âge",
    }
)


def style_finding(value):

    if value == "NC Majeure":
        return (
            f"background-color:{RED};"
            "color:white;"
            "font-weight:850;"
        )

    if value == "NC Mineure":
        return (
            f"background-color:{PEACH};"
            f"color:{MIDNIGHT_BLUE};"
            "font-weight:800;"
        )

    if value == "Observation":
        return (
            f"background-color:{SKY};"
            f"color:{ROYAL};"
            "font-weight:800;"
        )

    if value == "OFI":
        return (
            f"background-color:{GOLD};"
            f"color:{MIDNIGHT_BLUE};"
            "font-weight:800;"
        )

    if value == "Bonne Pratique":
        return (
            f"background-color:{SOFT_BLUE};"
            f"color:{ROYAL};"
            "font-weight:800;"
        )

    return ""


def style_age(value):

    if value == "Normal":
        return (
            f"background-color:{SKY};"
            f"color:{ROYAL};"
            "font-weight:800;"
        )

    if value == "Alerte":
        return (
            f"background-color:{GOLD};"
            f"color:{MIDNIGHT_BLUE};"
            "font-weight:800;"
        )

    if value == "Critique":
        return (
            f"background-color:{PEACH};"
            f"color:{MIDNIGHT_BLUE};"
            "font-weight:850;"
        )

    if value == "Escalade management":
        return (
            f"background-color:{RED};"
            "color:white;"
            "font-weight:900;"
        )

    return ""


styled_detail = (
    detail_table.style

    .format(
        {
            "Score": lambda x:
                "—"
                if pd.isna(x)
                else f"{x:.0f}",

            "Âge": lambda x:
                "—"
                if pd.isna(x)
                else f"{int(x)}",
        }
    )

    .set_table_styles(
        [
            {
                "selector": "thead th",
                "props": [
                    (
                        "background-color",
                        MIDNIGHT_BLUE,
                    ),
                    (
                        "color",
                        "white",
                    ),
                    (
                        "font-weight",
                        "800",
                    ),
                ],
            }
        ]
    )

    .map(
        style_finding,
        subset=["Finding"],
    )

    .map(
        style_age,
        subset=[
            "Indicateur âge"
        ],
    )
)


st.dataframe(
    styled_detail,
    use_container_width=True,
    hide_index=True,
    height=650,
)