import pandas as pd
import plotly.express as px
import streamlit as st

from data.loaders import (
    load_audit_overview,
    load_findings,
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
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Synthèse Exécutive | QIP",
    page_icon="📊",
    layout="wide",
)

apply_global_theme()
render_sidebar()


# =====================================================
# HELPERS
# =====================================================

STATUS_LABELS = {
    "audite": "Audité",
    "en_cours": "En cours",
    "non_audite": "Non démarré",
}



# =====================================================
# DATA
# =====================================================

audit_df = load_audit_overview()
findings_df = load_findings()


# =====================================================
# HEADER
# =====================================================

render_header(
    "Synthèse Exécutive",
    "Quality Health Checks — Vue globale de la campagne d'audit",
)

# =====================================================
# FILTRES
# =====================================================

st.markdown(
    '<div class="section-title">Filtres</div>',
    unsafe_allow_html=True,
)

filter_col1, filter_col2, filter_col3 = st.columns(3)

campaign_values = sorted(
    audit_df["campaign_name"]
    .dropna()
    .unique()
    .tolist()
)

account_values = sorted(
    audit_df["account_name"]
    .dropna()
    .unique()
    .tolist()
)


with filter_col1:
    selected_campaign = st.selectbox(
        "Campagne",
        ["Toutes"] + campaign_values,
    )


with filter_col2:
    selected_account = st.selectbox(
        "Compte",
        ["Tous"] + account_values,
    )


with filter_col3:
    selected_status_label = st.selectbox(
        "Statut audit",
        [
            "Tous",
            "Audité",
            "En cours",
            "Non démarré",
        ],
    )


# =====================================================
# APPLICATION DES FILTRES
# =====================================================

filtered_audit = audit_df.copy()


if selected_campaign != "Toutes":
    filtered_audit = filtered_audit[
        filtered_audit["campaign_name"]
        == selected_campaign
    ]


if selected_account != "Tous":
    filtered_audit = filtered_audit[
        filtered_audit["account_name"]
        == selected_account
    ]


if selected_status_label != "Tous":

    reverse_status = {
        value: key
        for key, value in STATUS_LABELS.items()
    }

    selected_status = reverse_status[
        selected_status_label
    ]

    filtered_audit = filtered_audit[
        filtered_audit[
            "official_audit_status"
        ]
        == selected_status
    ]


allowed_accounts = (
    filtered_audit["account_id"]
    .dropna()
    .unique()
)

allowed_campaigns = (
    filtered_audit["campaign_id"]
    .dropna()
    .unique()
)


filtered_findings = findings_df[
    findings_df["account_id"].isin(
        allowed_accounts
    )
    & findings_df["campaign_id"].isin(
        allowed_campaigns
    )
].copy()


# =====================================================
# KPI
# =====================================================

audits_planifies = (
    filtered_audit["account_id"]
    .nunique()
)


audites = (
    filtered_audit[
        filtered_audit["official_audit_status"]
        == "audite"
    ]["account_id"]
    .nunique()
)


en_cours = (
    filtered_audit[
        filtered_audit["official_audit_status"]
        == "en_cours"
    ]["account_id"]
    .nunique()
)


non_demarres = (
    filtered_audit[
        filtered_audit["official_audit_status"]
        == "non_audite"
    ]["account_id"]
    .nunique()
)


avancement = (
    audites / audits_planifies * 100
    if audits_planifies > 0
    else 0
)


audited_rows = filtered_audit[
    filtered_audit["official_audit_status"]
    == "audite"
]


score_moyen = (
    audited_rows["avg_maturity_score"].mean()
    if not audited_rows.empty
    else None
)


real_findings = filtered_findings[
    filtered_findings[
        "is_counted_in_total_findings"
    ]
    == True
]


total_findings = len(
    real_findings
)


nc_majeures = len(
    filtered_findings[
        filtered_findings[
            "categorie_finding"
        ]
        == "NC Majeure"
    ]
)


# =====================================================
# KPI CARDS — LIGNE 1
# =====================================================

st.markdown(
    '<div class="section-title">Indicateurs clés</div>',
    unsafe_allow_html=True,
)

k1, k2, k3, k4, k5 = st.columns(5)


with k1:
    kpi_card(
        "Audits planifiés",
        audits_planifies,
        MIDNIGHT_BLUE,
        "#EDEEF2",
    )


with k2:
    kpi_card(
        "Audités",
        audites,
        ROYAL,
        SOFT_BLUE,
    )


with k3:
    kpi_card(
        "En cours",
        en_cours,
        GOLD,
        SOFT_GOLD,
    )


with k4:
    kpi_card(
        "Non démarrés",
        non_demarres,
        CHARCOAL,
        SOFT_GRAY,
    )


with k5:
    kpi_card(
        "% Avancement",
        f"{avancement:.0f} %",
        ROYAL,
        SKY,
    )


st.markdown("<br>", unsafe_allow_html=True)


# =====================================================
# KPI CARDS — LIGNE 2
# =====================================================

k6, k7, k8 = st.columns(3)


with k6:

    score_display = (
        f"{score_moyen:.2f} / 5"
        if score_moyen is not None
        and not pd.isna(score_moyen)
        else "—"
    )

    kpi_card(
        "Score moyen maturité",
        score_display,
        ROYAL,
        SOFT_SKY,
    )


with k7:
    kpi_card(
        "Total Findings",
        total_findings,
        GOLD,
        PEACH,
    )


with k8:
    kpi_card(
        "NC Majeures",
        nc_majeures,
        RED,
        SOFT_RED,
    )


st.markdown("<br>", unsafe_allow_html=True)


# =====================================================
# GRAPHIQUES
# =====================================================

st.markdown(
    '<div class="section-title">Analyse visuelle</div>',
    unsafe_allow_html=True,
)

left_chart, right_chart = st.columns(2)


# -----------------------------------------------------
# Répartition statuts
# -----------------------------------------------------

with left_chart:

    st.markdown(
        '<div class="chart-card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        "### Répartition des statuts officiels"
    )

    status_counts = (
        filtered_audit[
            "official_audit_status"
        ]
        .value_counts()
        .rename_axis(
            "official_audit_status"
        )
        .reset_index(
            name="Nombre"
        )
    )

    status_counts["Statut"] = (
        status_counts[
            "official_audit_status"
        ]
        .map(
            STATUS_LABELS
        )
    )

    fig_status = px.pie(
        status_counts,
        names="Statut",
        values="Nombre",
        hole=0.62,
        color="Statut",
        color_discrete_map={
            "Audité": ROYAL,
            "En cours": GOLD,
            "Non démarré": "#7B8794",
        },
    )

    fig_status.update_traces(
        textposition="inside",
        textinfo="value+percent",
        marker=dict(
            line=dict(
                color="white",
                width=2,
            )
        ),
    )

    fig_status.update_layout(
        showlegend=True,
        legend_title_text="",
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color=MIDNIGHT_BLUE
        ),
    )

    st.plotly_chart(
        fig_status,
        use_container_width=True,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------
# Findings par compte
# -----------------------------------------------------

with right_chart:

    st.markdown(
        '<div class="chart-card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        "### Findings par compte"
    )

    findings_by_account = (
        real_findings
        .groupby(
            "account_name",
            as_index=False,
        )
        .size()
        .rename(
            columns={
                "size": "Total Findings"
            }
        )
        .sort_values(
            "Total Findings",
            ascending=True,
        )
    )

    fig_findings = px.bar(
        findings_by_account,
        x="Total Findings",
        y="account_name",
        orientation="h",
        text="Total Findings",
    )

    fig_findings.update_traces(
        marker_color=ROYAL,
        textposition="outside",
        marker_line_color=MIDNIGHT_BLUE,
        marker_line_width=0.5,
    )

    fig_findings.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(
            l=10,
            r=40,
            t=10,
            b=10,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=SOFT_SKY,
        font=dict(
            color=MIDNIGHT_BLUE
        ),
    )

    fig_findings.update_xaxes(
        gridcolor="#D9EAF7"
    )

    st.plotly_chart(
        fig_findings,
        use_container_width=True,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# =====================================================
# TABLEAU GLOBAL
# =====================================================

# =====================================================
# TABLEAU GLOBAL
# =====================================================

st.markdown(
    '<div class="section-title">'
    'Vue globale des comptes'
    '</div>',
    unsafe_allow_html=True,
)


table_df = filtered_audit[
    [
        "account_name",
        "official_audit_status",
        "completion_rate",
        "avg_maturity_score",
        "account_badge",
        "total_findings_kpi",
        "open_action_count",
        "escalated_action_count",
    ]
].copy()


table_df[
    "official_audit_status"
] = table_df[
    "official_audit_status"
].map(
    STATUS_LABELS
)


table_df = table_df.rename(
    columns={
        "account_name": "Compte",
        "official_audit_status": "Statut officiel",
        "completion_rate": "% Avancement",
        "avg_maturity_score": "Score moyen",
        "account_badge": "Badge",
        "total_findings_kpi": "Total Findings",
        "open_action_count": "Actions ouvertes",
        "escalated_action_count": "Escalades",
    }
)


# =====================================================
# STYLES DU TABLEAU
# =====================================================

def style_status(value):

    if value == "Audité":
        return (
            "background-color: #A1E6FF;"
            "color: #004AAC;"
            "font-weight: 700;"
        )

    if value == "En cours":
        return (
            "background-color: #FFAE41;"
            "color: #0E1020;"
            "font-weight: 700;"
        )

    if value == "Non démarré":
        return (
            "background-color: #E4E5E8;"
            "color: #2B2B2B;"
            "font-weight: 700;"
        )

    return ""


def style_badge(value):

    if pd.isna(value):
        return ""

    value = str(value)

    if value == "Très Performant":
        return (
            "background-color: #A1E6FF;"
            "color: #004AAC;"
            "font-weight: 700;"
        )

    if value == "Performant":
        return (
            "background-color: #D9ECFF;"
            "color: #004AAC;"
            "font-weight: 700;"
        )

    if value in [
        "En Progression",
        "À surveiller",
        "À Surveiller",
    ]:
        return (
            "background-color: #FFAE41;"
            "color: #0E1020;"
            "font-weight: 700;"
        )

    if value in [
        "À Risque",
        "A Risque",
    ]:
        return (
            "background-color: #FFC082;"
            "color: #2B2B2B;"
            "font-weight: 700;"
        )

    if value == "Critique":
        return (
            "background-color: #D94000;"
            "color: white;"
            "font-weight: 700;"
        )

    return ""


def style_score(value):

    if pd.isna(value):
        return (
            "background-color: #F0F1F3;"
            "color: #777777;"
        )

    if value >= 4.5:
        return (
            "background-color: #A1E6FF;"
            "color: #004AAC;"
            "font-weight: 700;"
        )

    if value >= 3.5:
        return (
            "background-color: #D9ECFF;"
            "color: #004AAC;"
            "font-weight: 700;"
        )

    if value >= 2.5:
        return (
            "background-color: #FFF0D6;"
            "color: #2B2B2B;"
            "font-weight: 700;"
        )

    if value >= 1.5:
        return (
            "background-color: #FFC082;"
            "color: #2B2B2B;"
            "font-weight: 700;"
        )

    return (
        "background-color: #D94000;"
        "color: white;"
        "font-weight: 700;"
    )


def style_findings(value):

    if pd.isna(value) or value == 0:
        return (
            "background-color: #F0F1F3;"
            "color: #777777;"
        )

    if value >= 7:
        return (
            "background-color: #D94000;"
            "color: white;"
            "font-weight: 700;"
        )

    if value >= 4:
        return (
            "background-color: #FFC082;"
            "color: #2B2B2B;"
            "font-weight: 700;"
        )

    return (
        "background-color: #FFF0D6;"
        "color: #2B2B2B;"
        "font-weight: 700;"
    )


def style_escalades(value):

    if pd.isna(value) or value == 0:
        return (
            "background-color: #EAF3FF;"
            "color: #004AAC;"
            "font-weight: 700;"
        )

    return (
        "background-color: #D94000;"
        "color: white;"
        "font-weight: 800;"
    )


styled_table = (
    table_df.style

    # En-tête DXC
    .set_table_styles(
        [
            {
                "selector": "thead th",
                "props": [
                    ("background-color", MIDNIGHT_BLUE),
                    ("color", "white"),
                    ("font-weight", "700"),
                    ("text-align", "center"),
                ],
            },

            {
                "selector": "tbody td",
                "props": [
                    ("border-bottom", "1px solid #E7E7E7"),
                    ("padding", "9px"),
                ],
            },
        ]
    )

    # Compte
    .set_properties(
        subset=["Compte"],
        **{
            "font-weight": "700",
            "color": MIDNIGHT_BLUE,
            "background-color": "#F7FBFF",
        }
    )

    # Statut
    .map(
        style_status,
        subset=["Statut officiel"],
    )

    # Score
    .map(
        style_score,
        subset=["Score moyen"],
    )

    # Badge
    .map(
        style_badge,
        subset=["Badge"],
    )

    # Findings
    .map(
        style_findings,
        subset=["Total Findings"],
    )

    # Escalades
    .map(
        style_escalades,
        subset=["Escalades"],
    )

    # Centrer les colonnes numériques
    .set_properties(
        subset=[
            "% Avancement",
            "Score moyen",
            "Total Findings",
            "Actions ouvertes",
            "Escalades",
        ],
        **{
            "text-align": "center",
        }
    )
)


st.dataframe(
    styled_table,
    use_container_width=True,
    hide_index=True,
    height=570,
    column_config={
        "% Avancement": st.column_config.ProgressColumn(
            "% Avancement",
            help="Taux de complétude des évaluations du compte",
            min_value=0,
            max_value=100,
            format="%.1f %%",
        ),

        "Score moyen": st.column_config.NumberColumn(
            "Score moyen",
            format="%.2f",
        ),

        "Total Findings": st.column_config.NumberColumn(
            "Total Findings",
            format="%d",
        ),

        "Actions ouvertes": st.column_config.NumberColumn(
            "Actions ouvertes",
            format="%d",
        ),

        "Escalades": st.column_config.NumberColumn(
            "Escalades",
            format="%d",
        ),
    },
)