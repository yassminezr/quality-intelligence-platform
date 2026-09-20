import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.loaders import (
    load_audit_overview,
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
    page_title="Findings & Actions | QIP",
    page_icon="⚠️",
    layout="wide",
)

apply_global_theme()
render_sidebar()

render_header(
    "Findings & Actions Correctives",
    "Pilotage des non-conformités et suivi des plans d’action",
)


# =====================================================
# HELPERS
# =====================================================

CATEGORY_COLORS = {
    "NC Mineure": PEACH,
    "NC Majeure": RED,
    "Observation": SKY,
    "OFI": GOLD,
    "Bonne Pratique": ROYAL,
    "NA": "#A0A5AE",
}

# =====================================================
# DATA
# =====================================================

audit_df = load_audit_overview()
findings_df = load_findings()
actions_df = load_corrective_actions()


# =====================================================
# FILTRES
# =====================================================

st.markdown(
    '<div class="section-title">Filtres</div>',
    unsafe_allow_html=True,
)

f1, f2, f3, f4 = st.columns(4)

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

finding_values = sorted(
    findings_df["categorie_finding"]
    .dropna()
    .unique()
    .tolist()
)

action_status_values = sorted(
    actions_df["statut"]
    .dropna()
    .unique()
    .tolist()
)


with f1:
    selected_campaign = st.selectbox(
        "Campagne",
        ["Toutes"] + campaign_values,
    )


with f2:
    selected_account = st.selectbox(
        "Compte",
        ["Tous"] + account_values,
    )


with f3:
    selected_finding = st.selectbox(
        "Catégorie finding",
        ["Toutes"] + finding_values,
    )


with f4:
    selected_action_status = st.selectbox(
        "Statut action",
        ["Tous"] + action_status_values,
    )


# =====================================================
# FILTERING
# =====================================================

filtered_findings = findings_df.copy()
filtered_actions = actions_df.copy()


if selected_campaign != "Toutes":

    filtered_findings = filtered_findings[
        filtered_findings["campaign_name"]
        == selected_campaign
    ]

    filtered_actions = filtered_actions[
        filtered_actions["campaign_name"]
        == selected_campaign
    ]


if selected_account != "Tous":

    filtered_findings = filtered_findings[
        filtered_findings["account_name"]
        == selected_account
    ]

    filtered_actions = filtered_actions[
        filtered_actions["account_name"]
        == selected_account
    ]


if selected_finding != "Toutes":

    filtered_findings = filtered_findings[
        filtered_findings["categorie_finding"]
        == selected_finding
    ]

    filtered_actions = filtered_actions[
        filtered_actions["categorie_finding"]
        == selected_finding
    ]


if selected_action_status != "Tous":

    filtered_actions = filtered_actions[
        filtered_actions["statut"]
        == selected_action_status
    ]


# =====================================================
# KPI
# =====================================================

counted_findings = filtered_findings[
    filtered_findings[
        "is_counted_in_total_findings"
    ] == True
]


total_findings = len(
    counted_findings
)

nc_mineures = len(
    filtered_findings[
        filtered_findings["categorie_finding"]
        == "NC Mineure"
    ]
)

nc_majeures = len(
    filtered_findings[
        filtered_findings["categorie_finding"]
        == "NC Majeure"
    ]
)

observations = len(
    filtered_findings[
        filtered_findings["categorie_finding"]
        == "Observation"
    ]
)

ofi = len(
    filtered_findings[
        filtered_findings["categorie_finding"]
        == "OFI"
    ]
)

bonnes_pratiques = len(
    filtered_findings[
        filtered_findings["categorie_finding"]
        == "Bonne Pratique"
    ]
)

actions_ouvertes = len(
    filtered_actions[
        filtered_actions["is_open"]
        == True
    ]
)

escalades = len(
    filtered_actions[
        filtered_actions["indicateur_age"]
        == "Escalade management"
    ]
)


# =====================================================
# KPI CARDS
# =====================================================

st.markdown(
    '<div class="section-title">Indicateurs clés</div>',
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)

with k1:
    kpi_card(
        "Total Findings",
        total_findings,
        MIDNIGHT_BLUE,
        SOFT_BLUE,
    )

with k2:
    kpi_card(
        "NC Mineures",
        nc_mineures,
        PEACH,
        SOFT_GOLD,
    )

with k3:
    kpi_card(
        "NC Majeures",
        nc_majeures,
        RED,
        SOFT_RED,
    )

with k4:
    kpi_card(
        "Observations",
        observations,
        ROYAL,
        SOFT_SKY,
    )


st.markdown("<br>", unsafe_allow_html=True)


k5, k6, k7, k8 = st.columns(4)

with k5:
    kpi_card(
        "OFI",
        ofi,
        GOLD,
        SOFT_GOLD,
    )

with k6:
    kpi_card(
        "Bonnes Pratiques",
        bonnes_pratiques,
        ROYAL,
        SKY,
    )

with k7:
    kpi_card(
        "Actions ouvertes",
        actions_ouvertes,
        PEACH,
        SOFT_GOLD,
    )

with k8:
    kpi_card(
        "Escalades",
        escalades,
        RED,
        SOFT_RED,
    )


# =====================================================
# GRAPHIQUES PRINCIPAUX
# =====================================================

st.markdown(
    '<div class="section-title">Analyse des findings</div>',
    unsafe_allow_html=True,
)

left, right = st.columns(2)


# -----------------------------------------------------
# FINDINGS PAR COMPTE — STACKED
# -----------------------------------------------------

with left:

    findings_by_account = (
        filtered_findings
        .groupby(
            [
                "account_name",
                "categorie_finding",
            ]
        )
        .size()
        .reset_index(
            name="Nombre"
        )
    )


    fig_account = px.bar(
        findings_by_account,
        x="Nombre",
        y="account_name",
        color="categorie_finding",
        orientation="h",

        color_discrete_map=CATEGORY_COLORS,

        labels={
            "account_name": "Compte",
            "categorie_finding": "Catégorie",
        },
    )


    fig_account.update_layout(
        title="Findings par compte",
        barmode="stack",
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#F8FBFF",
        legend_title_text="",
        font=dict(
            color=MIDNIGHT_BLUE
        ),
    )


    st.plotly_chart(
        fig_account,
        use_container_width=True,
    )


# -----------------------------------------------------
# DONUT CATEGORIES
# -----------------------------------------------------

with right:

    category_counts = (
        filtered_findings[
            "categorie_finding"
        ]
        .value_counts()
        .rename_axis(
            "Catégorie"
        )
        .reset_index(
            name="Nombre"
        )
    )


    fig_cat = px.pie(
        category_counts,
        names="Catégorie",
        values="Nombre",
        hole=0.60,
        color="Catégorie",
        color_discrete_map=CATEGORY_COLORS,
    )


    fig_cat.update_traces(
        textinfo="value+percent",
        textposition="inside",
        marker=dict(
            line=dict(
                color="white",
                width=2,
            )
        ),
    )


    fig_cat.update_layout(
        title="Répartition des catégories",
        legend_title_text="",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color=MIDNIGHT_BLUE
        ),
    )


    st.plotly_chart(
        fig_cat,
        use_container_width=True,
    )


# =====================================================
# ANCIENNETE ACTIONS
# =====================================================

st.markdown(
    '<div class="section-title">'
    'Ancienneté des actions correctives'
    '</div>',
    unsafe_allow_html=True,
)


age_order = [
    "Normal",
    "Alerte",
    "Critique",
    "Escalade management",
]


age_counts = (
    filtered_actions[
        "indicateur_age"
    ]
    .dropna()
    .value_counts()
    .reindex(
        age_order,
        fill_value=0,
    )
    .reset_index()
)


age_counts.columns = [
    "Indicateur",
    "Nombre",
]


age_colors = {
    "Normal": SKY,
    "Alerte": GOLD,
    "Critique": PEACH,
    "Escalade management": RED,
}


fig_age = px.bar(
    age_counts,
    x="Indicateur",
    y="Nombre",
    text="Nombre",
    color="Indicateur",
    color_discrete_map=age_colors,
)


fig_age.update_traces(
    textposition="outside",
)


fig_age.update_layout(
    showlegend=False,
    xaxis_title=None,
    yaxis_title="Nombre d'actions",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FFF9F2",
    font=dict(
        color=MIDNIGHT_BLUE
    ),
)


st.plotly_chart(
    fig_age,
    use_container_width=True,
)


# =====================================================
# FINDINGS PAR CLAUSE ISO
# =====================================================

st.markdown(
    '<div class="section-title">'
    'Findings par clause ISO'
    '</div>',
    unsafe_allow_html=True,
)


clause_pivot = (
    filtered_findings
    .pivot_table(
        index=[
            "clause_iso",
            "libelle_terrain",
        ],
        columns="categorie_finding",
        values="finding_id",
        aggfunc="count",
        fill_value=0,
    )
    .reset_index()
)


required_cols = [
    "NC Majeure",
    "NC Mineure",
    "Observation",
    "OFI",
]


for col in required_cols:
    if col not in clause_pivot.columns:
        clause_pivot[col] = 0


for col in required_cols:
    clause_pivot[col] = (
        clause_pivot[col]
        .fillna(0)
        .astype(int)
    )


clause_pivot["Total"] = (
    clause_pivot["NC Majeure"]
    + clause_pivot["NC Mineure"]
    + clause_pivot["Observation"]
    + clause_pivot["OFI"]
)


clause_table = clause_pivot[
    [
        "clause_iso",
        "libelle_terrain",
        "NC Majeure",
        "NC Mineure",
        "Observation",
        "OFI",
        "Total",
    ]
].copy()


clause_table = clause_table.rename(
    columns={
        "clause_iso": "Clause",
        "libelle_terrain": "Libellé Terrain",
        "NC Majeure": "NC Maj",
        "NC Mineure": "NC Min",
        "Observation": "Obs",
    }
)


clause_table = clause_table.sort_values(
    "Total",
    ascending=False,
)


# =====================================================
# COLOR TABLE
# =====================================================

def style_nc_maj(value):

    if value > 0:
        return (
            f"background-color:{RED};"
            "color:white;"
            "font-weight:900;"
        )

    return "color:#999999;"


def style_nc_min(value):

    if value > 0:
        return (
            f"background-color:{PEACH};"
            f"color:{MIDNIGHT_BLUE};"
            "font-weight:800;"
        )

    return "color:#999999;"


def style_obs(value):

    if value > 0:
        return (
            f"background-color:{SKY};"
            f"color:{ROYAL};"
            "font-weight:800;"
        )

    return "color:#999999;"


def style_ofi(value):

    if value > 0:
        return (
            f"background-color:{GOLD};"
            f"color:{MIDNIGHT_BLUE};"
            "font-weight:800;"
        )

    return "color:#999999;"


def style_total(value):

    if value >= 7:
        return (
            f"background-color:{RED};"
            "color:white;"
            "font-weight:900;"
        )

    if value >= 4:
        return (
            f"background-color:{PEACH};"
            f"color:{MIDNIGHT_BLUE};"
            "font-weight:900;"
        )

    if value > 0:
        return (
            f"background-color:{SOFT_GOLD};"
            f"color:{MIDNIGHT_BLUE};"
            "font-weight:800;"
        )

    return ""


styled_clause = (
    clause_table.style

    .format(
        {
            "NC Maj": "{:d}",
            "NC Min": "{:d}",
            "Obs": "{:d}",
            "OFI": "{:d}",
            "Total": "{:d}",
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
                    (
                        "text-align",
                        "center",
                    ),
                ],
            }
        ]
    )

    .map(
        style_nc_maj,
        subset=["NC Maj"],
    )

    .map(
        style_nc_min,
        subset=["NC Min"],
    )

    .map(
        style_obs,
        subset=["Obs"],
    )

    .map(
        style_ofi,
        subset=["OFI"],
    )

    .map(
        style_total,
        subset=["Total"],
    )
)


st.dataframe(
    styled_clause,
    use_container_width=True,
    hide_index=True,
    height=430,
)


# =====================================================
# TOP FINDINGS
# =====================================================

st.markdown(
    '<div class="section-title">'
    'Top Findings'
    '</div>',
    unsafe_allow_html=True,
)


top_findings = (
    clause_table[
        clause_table["Total"] > 0
    ]
    .nlargest(
        10,
        "Total",
    )
    .sort_values(
        "Total",
        ascending=True,
    )
)


fig_top = px.bar(
    top_findings,
    x="Total",
    y="Libellé Terrain",
    orientation="h",
    text="Total",
)


fig_top.update_traces(
    marker_color=GOLD,
    marker_line_color=PEACH,
    marker_line_width=1,
    textposition="outside",
)


fig_top.update_layout(
    xaxis_title=None,
    yaxis_title=None,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FFF9F2",
    font=dict(
        color=MIDNIGHT_BLUE
    ),
)


st.plotly_chart(
    fig_top,
    use_container_width=True,
)


# =====================================================
# ACTIONS PRIORITAIRES
# =====================================================

st.markdown(
    '<div class="section-title">'
    'Actions prioritaires'
    '</div>',
    unsafe_allow_html=True,
)


priority_actions = filtered_actions[
    [
        "account_name",
        "action_text",
        "responsable",
        "statut",
        "age_jours",
        "indicateur_age",
    ]
].copy()


priority_rank = {
    "Escalade management": 4,
    "Critique": 3,
    "Alerte": 2,
    "Normal": 1,
}


priority_actions[
    "priority_rank"
] = (
    priority_actions[
        "indicateur_age"
    ]
    .map(
        priority_rank
    )
    .fillna(0)
)


priority_actions = (
    priority_actions
    .sort_values(
        [
            "priority_rank",
            "age_jours",
        ],
        ascending=[
            False,
            False,
        ],
    )
    .drop(
        columns=[
            "priority_rank"
        ]
    )
)


priority_actions = priority_actions.rename(
    columns={
        "account_name": "Compte",
        "action_text": "Action corrective",
        "responsable": "Responsable",
        "statut": "Statut",
        "age_jours": "Âge (jours)",
        "indicateur_age": "Indicateur âge",
    }
)


def style_age_indicator(value):

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


styled_actions = (
    priority_actions.style

    .format(
        {
            "Âge (jours)": lambda x:
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
        style_age_indicator,
        subset=[
            "Indicateur âge"
        ],
    )
)


st.dataframe(
    styled_actions,
    use_container_width=True,
    hide_index=True,
    height=500,
)