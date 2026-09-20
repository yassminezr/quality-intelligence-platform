import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.loaders import (
    load_audit_overview,
    load_account_clause_detail,
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
    page_title="Maturité & Performance | QIP",
    page_icon="📈",
    layout="wide",
)

apply_global_theme()
render_sidebar()

render_header(
    "Maturité & Performance",
    "Analyse de la maturité ISO 9001 et comparaison des comptes",
)


# =====================================================
# HELPERS
# =====================================================

STATUS_LABELS = {
    "audite": "Audité",
    "en_cours": "En cours",
    "non_audite": "Non démarré",
}


def get_chapter(clause):
    if pd.isna(clause):
        return None

    clause = str(clause).strip()

    if not clause:
        return None

    return clause.split(".")[0]


# =====================================================
# DATA
# =====================================================

audit_df = load_audit_overview()
detail_df = load_account_clause_detail()
findings_df = load_findings()


# =====================================================
# FILTRES
# =====================================================

st.markdown(
    '<div class="section-title">Filtres</div>',
    unsafe_allow_html=True,
)

f1, f2, f3 = st.columns(3)

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
# FILTRAGE
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
        v: k
        for k, v in STATUS_LABELS.items()
    }

    status_value = reverse_status[
        selected_status_label
    ]

    filtered_audit = filtered_audit[
        filtered_audit["official_audit_status"]
        == status_value
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


filtered_detail = detail_df[
    detail_df["account_id"].isin(
        allowed_accounts
    )
    & detail_df["campaign_id"].isin(
        allowed_campaigns
    )
].copy()


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

score_global = (
    filtered_detail["score_maturite"]
    .dropna()
    .mean()
)


badge_counts = (
    filtered_audit["account_badge"]
    .dropna()
    .value_counts()
)


nb_tres_performants = int(
    badge_counts.get(
        "Très Performant",
        0,
    )
)

nb_performants = int(
    badge_counts.get(
        "Performant",
        0,
    )
)

nb_progression = int(
    badge_counts.get(
        "En Progression",
        badge_counts.get(
            "À surveiller",
            0,
        ),
    )
)

nb_risque = int(
    badge_counts.get(
        "À Risque",
        0,
    )
)


st.markdown(
    '<div class="section-title">Indicateurs clés</div>',
    unsafe_allow_html=True,
)


k1, k2, k3, k4, k5 = st.columns(5)


with k1:
    score_display = (
        f"{score_global:.2f} / 5"
        if pd.notna(score_global)
        else "—"
    )

    kpi_card(
        "Score moyen",
        score_display,
        ROYAL,
        SOFT_SKY,
    )


with k2:
    kpi_card(
        "Très performants",
        nb_tres_performants,
        ROYAL,
        SKY,
    )


with k3:
    kpi_card(
        "Performants",
        nb_performants,
        ROYAL,
        SOFT_BLUE,
    )


with k4:
    kpi_card(
        "En progression",
        nb_progression,
        GOLD,
        SOFT_GOLD,
    )


with k5:
    kpi_card(
        "À risque",
        nb_risque,
        RED,
        SOFT_RED,
    )


# =====================================================
# SCORE PAR COMPTE
# =====================================================

st.markdown(
    '<div class="section-title">'
    'Score moyen de maturité par compte'
    '</div>',
    unsafe_allow_html=True,
)


score_by_account = (
    filtered_audit[
        [
            "account_name",
            "avg_maturity_score",
            "account_badge",
        ]
    ]
    .dropna(
        subset=["avg_maturity_score"]
    )
    .sort_values(
        "avg_maturity_score",
        ascending=True,
    )
)


def score_color(score):

    if score >= 4.5:
        return SKY

    if score >= 3.5:
        return ROYAL

    if score >= 2.5:
        return GOLD

    if score >= 1.5:
        return PEACH

    return RED


score_by_account["Couleur"] = (
    score_by_account[
        "avg_maturity_score"
    ]
    .apply(score_color)
)


fig_score = go.Figure()


fig_score.add_trace(
    go.Bar(
        x=score_by_account[
            "avg_maturity_score"
        ],
        y=score_by_account[
            "account_name"
        ],
        orientation="h",

        marker_color=score_by_account[
            "Couleur"
        ],

        text=score_by_account[
            "avg_maturity_score"
        ].round(2),

        textposition="outside",
    )
)


fig_score.update_layout(
    height=500,
    xaxis_title="Score moyen",
    yaxis_title=None,
    xaxis=dict(
        range=[0, 5],
        gridcolor="#D9EAF7",
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#F7FBFF",
    font=dict(
        color=MIDNIGHT_BLUE
    ),
)


st.plotly_chart(
    fig_score,
    use_container_width=True,
)


# =====================================================
# DISTRIBUTION MATURITE
# =====================================================

st.markdown(
    '<div class="section-title">'
    'Distribution des niveaux de maturité'
    '</div>',
    unsafe_allow_html=True,
)


level_distribution = (
    filtered_detail[
        "niveau_maturite"
    ]
    .dropna()
    .value_counts()
    .rename_axis(
        "Niveau"
    )
    .reset_index(
        name="Nombre"
    )
)


colors_levels = [
    ROYAL,
    SKY,
    GOLD,
    PEACH,
    RED,
]


fig_levels = px.bar(
    level_distribution,
    x="Niveau",
    y="Nombre",
    text="Nombre",
    color="Niveau",
    color_discrete_sequence=colors_levels,
)


fig_levels.update_traces(
    textposition="outside",
)


fig_levels.update_layout(
    showlegend=False,
    xaxis_title=None,
    yaxis_title="Nombre d'évaluations",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FFF9F2",
    font=dict(
        color=MIDNIGHT_BLUE
    ),
)


st.plotly_chart(
    fig_levels,
    use_container_width=True,
)


# =====================================================
# MATRICE CHAPITRE × COMPTE
# =====================================================

# =====================================================
# MATRICE CHAPITRE × COMPTE
# =====================================================

st.markdown(
    '<div class="section-title">'
    'Maturité par chapitre ISO × compte'
    '</div>',
    unsafe_allow_html=True,
)


chapter_df = filtered_detail.copy()


# -----------------------------------------------------
# Extraire le chapitre ISO
# -----------------------------------------------------

chapter_df["Chapitre_num"] = (
    chapter_df["clause_iso"]
    .astype(str)
    .str.extract(r"^(\d+)")[0]
)


chapter_df["Chapitre_num"] = pd.to_numeric(
    chapter_df["Chapitre_num"],
    errors="coerce",
)


# On garde uniquement ISO 9001 chapitres 4 à 10
chapter_df = chapter_df[
    chapter_df["Chapitre_num"].between(
        4,
        10,
    )
].copy()


# -----------------------------------------------------
# Calcul score moyen par chapitre / compte
# -----------------------------------------------------

chapter_matrix = (
    chapter_df
    .pivot_table(
        index="Chapitre_num",
        columns="account_name",
        values="score_maturite",
        aggfunc="mean",
    )
)


# -----------------------------------------------------
# Forcer l'ordre ISO
# -----------------------------------------------------

chapter_order = [
    4,
    5,
    6,
    7,
    8,
    9,
    10,
]


chapter_matrix = chapter_matrix.reindex(
    chapter_order
)


# Trier les comptes
chapter_matrix = chapter_matrix.reindex(
    sorted(
        chapter_matrix.columns
    ),
    axis=1,
)


# -----------------------------------------------------
# Labels
# -----------------------------------------------------

chapter_labels = [
    "Ch4 — Contexte",
    "Ch5 — Leadership",
    "Ch6 — Planification",
    "Ch7 — Support",
    "Ch8 — Réalisation",
    "Ch9 — Performance",
    "Ch10 — Amélioration",
]


# Texte affiché dans les cellules
text_matrix = (
    chapter_matrix
    .map(
        lambda value:
            f"{value:.2f}"
            if pd.notna(value)
            else "WIP"
    )
)


# =====================================================
# HEATMAP
# =====================================================

fig_heatmap = go.Figure(
    data=go.Heatmap(

        z=chapter_matrix.values,

        x=chapter_matrix.columns,

        # IMPORTANT :
        # texte catégoriel et non valeurs numériques
        y=chapter_labels,

        text=text_matrix.values,

        texttemplate="%{text}",

        colorscale=[
            [0.00, RED],
            [0.25, PEACH],
            [0.50, GOLD],
            [0.75, SKY],
            [1.00, ROYAL],
        ],

        zmin=1,
        zmax=5,

        colorbar=dict(
            title="Score",
            tickvals=[
                1,
                2,
                3,
                4,
                5,
            ],
        ),

        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{y}<br>"
            "Score : %{text}"
            "<extra></extra>"
        ),

        xgap=2,
        ygap=2,
    )
)


fig_heatmap.update_layout(

    height=500,

    paper_bgcolor="rgba(0,0,0,0)",

    plot_bgcolor="white",

    margin=dict(
        l=40,
        r=30,
        t=20,
        b=30,
    ),

    font=dict(
        color=MIDNIGHT_BLUE,
    ),

    xaxis=dict(
        title=None,
        side="bottom",
        tickangle=-25,
    ),

    yaxis=dict(
        title=None,

        # Ch4 en haut → Ch10 en bas
        autorange="reversed",

        type="category",
    ),
)


st.plotly_chart(
    fig_heatmap,
    use_container_width=True,
)


# =====================================================
# TABLE COMPARATIVE
# =====================================================

st.markdown(
    '<div class="section-title">'
    'Comparatif des comptes'
    '</div>',
    unsafe_allow_html=True,
)


findings_summary = (
    filtered_findings
    .pivot_table(
        index="account_name",
        columns="categorie_finding",
        values="finding_id",
        aggfunc="count",
        fill_value=0,
    )
    .reset_index()
)


# Colonnes obligatoires
finding_columns = [
    "NC Majeure",
    "NC Mineure",
    "Observation",
    "OFI",
    "Bonne Pratique",
]


for col in finding_columns:
    if col not in findings_summary.columns:
        findings_summary[col] = 0


comparative = filtered_audit[
    [
        "account_name",
        "avg_maturity_score",
        "account_badge",
        "total_findings_kpi",
    ]
].copy()


comparative = comparative.merge(
    findings_summary,
    on="account_name",
    how="left",
)


# =====================================================
# FORMAT NUMERIQUE
# =====================================================

count_cols = [
    "NC Majeure",
    "NC Mineure",
    "Observation",
    "OFI",
    "Bonne Pratique",
]


for col in count_cols:

    comparative[col] = (
        comparative[col]
        .fillna(0)
        .astype(int)
    )


comparative[
    "total_findings_kpi"
] = (
    comparative[
        "total_findings_kpi"
    ]
    .fillna(0)
    .astype(int)
)


comparative = comparative.rename(
    columns={
        "account_name": "Compte",
        "avg_maturity_score": "Score",
        "account_badge": "Badge",
        "NC Majeure": "NC Maj",
        "NC Mineure": "NC Min",
        "Observation": "Obs",
        "Bonne Pratique": "BP",
        "total_findings_kpi": "Total",
    }
)


comparative = comparative[
    [
        "Compte",
        "Score",
        "Badge",
        "NC Maj",
        "NC Min",
        "Obs",
        "OFI",
        "BP",
        "Total",
    ]
]


# =====================================================
# STYLING TABLE
# =====================================================

def style_score(value):

    if pd.isna(value):
        return (
            "background-color:#F0F1F3;"
            "color:#999999;"
        )

    if value >= 4.5:
        return (
            f"background-color:{SKY};"
            f"color:{ROYAL};"
            "font-weight:800;"
        )

    if value >= 3.5:
        return (
            "background-color:#DCEEFF;"
            f"color:{ROYAL};"
            "font-weight:800;"
        )

    if value >= 2.5:
        return (
            f"background-color:{GOLD};"
            f"color:{MIDNIGHT_BLUE};"
            "font-weight:800;"
        )

    if value >= 1.5:
        return (
            f"background-color:{PEACH};"
            f"color:{CHARCOAL};"
            "font-weight:800;"
        )

    return (
        f"background-color:{RED};"
        "color:white;"
        "font-weight:800;"
    )


def style_badge(value):

    if pd.isna(value):
        return (
            "background-color:#F0F1F3;"
            "color:#999999;"
        )

    value = str(value)

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

    if value in [
        "En Progression",
        "À surveiller",
        "À Surveiller",
    ]:
        return (
            f"background-color:{GOLD};"
            f"color:{MIDNIGHT_BLUE};"
            "font-weight:800;"
        )

    if value in [
        "À Risque",
        "A Risque",
    ]:
        return (
            f"background-color:{PEACH};"
            f"color:{CHARCOAL};"
            "font-weight:800;"
        )

    if value == "Critique":
        return (
            f"background-color:{RED};"
            "color:white;"
            "font-weight:800;"
        )

    return ""


def style_nc_major(value):

    if value > 0:
        return (
            f"background-color:{RED};"
            "color:white;"
            "font-weight:900;"
        )

    return (
        "background-color:#F4F4F4;"
        "color:#999999;"
    )


def style_nc_minor(value):

    if value >= 5:
        return (
            f"background-color:{PEACH};"
            f"color:{MIDNIGHT_BLUE};"
            "font-weight:800;"
        )

    if value > 0:
        return (
            f"background-color:{SOFT_GOLD};"
            f"color:{CHARCOAL};"
            "font-weight:700;"
        )

    return (
        "background-color:#F4F4F4;"
        "color:#999999;"
    )


def style_obs(value):

    if value > 0:
        return (
            f"background-color:{SKY};"
            f"color:{ROYAL};"
            "font-weight:700;"
        )

    return (
        "background-color:#F4F4F4;"
        "color:#999999;"
    )


def style_ofi(value):

    if value > 0:
        return (
            f"background-color:{GOLD};"
            f"color:{MIDNIGHT_BLUE};"
            "font-weight:700;"
        )

    return (
        "background-color:#F4F4F4;"
        "color:#999999;"
    )


def style_bp(value):

    if value > 0:
        return (
            f"background-color:{SKY};"
            f"color:{ROYAL};"
            "font-weight:750;"
        )

    return (
        "background-color:#F4F4F4;"
        "color:#999999;"
    )


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
            "font-weight:850;"
        )

    if value > 0:
        return (
            f"background-color:{SOFT_GOLD};"
            f"color:{MIDNIGHT_BLUE};"
            "font-weight:750;"
        )

    return (
        "background-color:#F0F1F3;"
        "color:#999999;"
    )


styled = (
    comparative.style

    .format(
        {
            "Score": lambda x:
                "—"
                if pd.isna(x)
                else f"{x:.2f}",

            "NC Maj": "{:d}",
            "NC Min": "{:d}",
            "Obs": "{:d}",
            "OFI": "{:d}",
            "BP": "{:d}",
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
            },

            {
                "selector": "tbody td",
                "props": [
                    (
                        "padding",
                        "10px",
                    ),
                    (
                        "border-bottom",
                        "1px solid #E6E6E6",
                    ),
                ],
            },
        ]
    )

    .set_properties(
        subset=["Compte"],
        **{
            "background-color": "#F7FBFF",
            "color": MIDNIGHT_BLUE,
            "font-weight": "800",
        }
    )

    .map(
        style_score,
        subset=["Score"],
    )

    .map(
        style_badge,
        subset=["Badge"],
    )

    .map(
        style_nc_major,
        subset=["NC Maj"],
    )

    .map(
        style_nc_minor,
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
        style_bp,
        subset=["BP"],
    )

    .map(
        style_total,
        subset=["Total"],
    )
)


st.dataframe(
    styled,
    use_container_width=True,
    hide_index=True,
    height=600,
)