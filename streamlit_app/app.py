import streamlit as st

from data.loaders import (
    load_audit_overview,
    load_findings,
    load_corrective_actions,
)

from styles.theme import (
    apply_global_theme,
    render_sidebar,
    kpi_card,
    MIDNIGHT_BLUE,
    ROYAL,
    SKY,
    RED,
    GOLD,
    SOFT_BLUE,
    SOFT_SKY,
    SOFT_GOLD,
    SOFT_RED,
)


# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Quality Intelligence Platform",
    page_icon="📊",
    layout="wide",
)

apply_global_theme()
render_sidebar()


# =====================================================
# DATA
# =====================================================

audit_df = load_audit_overview()
findings_df = load_findings()
actions_df = load_corrective_actions()


# =====================================================
# KPI GLOBAUX
# =====================================================

nb_comptes = (
    audit_df["account_id"]
    .nunique()
)

nb_audites = (
    audit_df[
        audit_df["official_audit_status"]
        == "audite"
    ]["account_id"]
    .nunique()
)

total_findings = len(
    findings_df[
        findings_df["is_counted_in_total_findings"]
        == True
    ]
)

actions_ouvertes = len(
    actions_df[
        actions_df["is_open"]
        == True
    ]
)


# =====================================================
# HERO
# =====================================================

hero_html = (
    f'<div class="hero">'
    f'<div class="hero-title">'
    f'Quality Intelligence Platform'
    f'</div>'
    f'<div class="hero-subtitle">'
    f'Pilotage intelligent des Quality Health Checks ISO 9001'
    f'</div>'
    f'</div>'
)

st.markdown(
    hero_html,
    unsafe_allow_html=True,
)


# =====================================================
# KPI RAPIDES
# =====================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    kpi_card(
        "Comptes",
        nb_comptes,
        MIDNIGHT_BLUE,
        SOFT_BLUE,
    )

with c2:
    kpi_card(
        "Audités",
        nb_audites,
        ROYAL,
        SOFT_SKY,
    )

with c3:
    kpi_card(
        "Total Findings",
        total_findings,
        GOLD,
        SOFT_GOLD,
    )

with c4:
    kpi_card(
        "Actions ouvertes",
        actions_ouvertes,
        RED,
        SOFT_RED,
    )


st.markdown(
    "<br>",
    unsafe_allow_html=True,
)


# =====================================================
# PRESENTATION DES PAGES
# =====================================================

st.subheader("Accès aux analyses")


def navigation_card(
    icon,
    title,
    description,
):
    html = (
        f'<div class="nav-card">'
        f'<div class="nav-title">'
        f'{icon} {title}'
        f'</div>'
        f'<div class="nav-text">'
        f'{description}'
        f'</div>'
        f'</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------
# Ligne 1
# -----------------------------------------------------

p1, p2 = st.columns(2)

with p1:

    navigation_card(
        "📊",
        "Synthèse Exécutive",
        (
            "Vue globale de la campagne : "
            "audits réalisés, audits en cours, "
            "avancement, maturité, findings "
            "et état global des comptes."
        ),
    )


with p2:

    navigation_card(
        "📈",
        "Maturité & Performance",
        (
            "Analyse des scores de maturité, "
            "badges de performance, distribution "
            "des niveaux et maturité par chapitre ISO."
        ),
    )


st.markdown(
    "<br>",
    unsafe_allow_html=True,
)


# -----------------------------------------------------
# Ligne 2
# -----------------------------------------------------

p3, p4 = st.columns(2)

with p3:

    navigation_card(
        "⚠️",
        "Findings & Actions",
        (
            "Analyse des non-conformités, "
            "observations, OFI, actions correctives, "
            "ancienneté et escalades."
        ),
    )


with p4:

    navigation_card(
        "🔎",
        "Détail Compte",
        (
            "Exploration détaillée d’un compte : "
            "score, badge, findings, maturité par chapitre, "
            "actions correctives et détail des clauses ISO."
        ),
    )


# =====================================================
# FOOTER
# =====================================================

st.markdown(
    "<br><br>",
    unsafe_allow_html=True,
)

st.caption(
    "Quality Intelligence Platform — QHC ISO 9001"
)