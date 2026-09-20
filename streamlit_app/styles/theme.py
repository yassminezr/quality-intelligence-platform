import streamlit as st


MIDNIGHT_BLUE = "#0E1020"
ROYAL = "#004AAC"
SKY = "#A1E6FF"
RED = "#D94000"
GOLD = "#FFAE41"
CANVAS = "#F6F3F0"
PEACH = "#FFC082"
CHARCOAL = "#2B2B2B"

SOFT_BLUE = "#EAF3FF"
SOFT_SKY = "#E9F9FF"
SOFT_GOLD = "#FFF4E3"
SOFT_RED = "#FFE8DF"
SOFT_GRAY = "#F0F1F3"


def apply_global_theme():
    st.markdown(
        f"""
        <style>

        .stApp {{
            background-color: {CANVAS};
        }}

        .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 1550px;
        }}

        section[data-testid="stSidebar"] {{
            background-color: {MIDNIGHT_BLUE};
        }}

        section[data-testid="stSidebar"] * {{
            color: white;
        }}

        section[data-testid="stSidebar"] a {{
            color: white !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {{
            border-radius: 10px;
            margin: 4px 8px;
        }}

        section[data-testid="stSidebar"] [aria-current="page"] {{
            background-color: {ROYAL};
        }}

        /* =================================================
           SIDEBAR PAGE LINKS
           ================================================= */

        section[data-testid="stSidebar"] div[data-testid="stPageLink"] a {{
            border-radius: 10px;
            padding: 8px 10px;
        }}

        section[data-testid="stSidebar"] div[data-testid="stPageLink"] a:hover {{
            background-color: {ROYAL};
        }}

        section[data-testid="stSidebar"] hr {{
            border-color: rgba(255,255,255,0.15);
        }}

        .qip-header {{
            background: linear-gradient(
                90deg,
                {MIDNIGHT_BLUE} 0%,
                {ROYAL} 100%
            );
            color: white;
            padding: 22px 30px;
            border-radius: 16px;
            margin-bottom: 20px;
            box-shadow: 0 5px 18px rgba(14,16,32,0.18);
        }}

        .qip-header-title {{
            font-size: 31px;
            font-weight: 850;
        }}

        .qip-header-subtitle {{
            color: {SKY};
            font-size: 16px;
            margin-top: 5px;
        }}

        .section-title {{
            color: {MIDNIGHT_BLUE};
            font-size: 22px;
            font-weight: 850;
            margin-top: 20px;
            margin-bottom: 12px;
            padding-left: 12px;
            border-left: 6px solid {ROYAL};
        }}

        .kpi-card {{
            border-radius: 17px;
            padding: 18px 20px;
            min-height: 115px;
            box-shadow: 0 4px 15px rgba(14,16,32,0.10);
            border: 1px solid rgba(14,16,32,0.05);
        }}

        .kpi-title {{
            color: #626A78;
            font-size: 13px;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}

        .kpi-value {{
            margin-top: 8px;
            font-size: 30px;
            font-weight: 900;
        }}

        div[data-testid="stDataFrame"] {{
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(14,16,32,0.10);
        }}

        div[data-baseweb="select"] > div {{
            border-radius: 10px;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():

    with st.sidebar:

        # =================================================
        # BRAND
        # =================================================

        brand_html = (
            '<div style="padding:8px 4px 8px 4px;">'
            '<div style="font-size:21px;font-weight:900;color:white;line-height:1.2;">'
            'Quality Intelligence'
            '</div>'
            '<div style="font-size:21px;font-weight:900;color:#A1E6FF;line-height:1.2;">'
            'Platform'
            '</div>'
            '<div style="margin-top:7px;font-size:12px;color:#A1E6FF;">'
            'QHC • ISO 9001'
            '</div>'
            '</div>'
        )

        st.markdown(
            brand_html,
            unsafe_allow_html=True,
        )

        st.divider()

        # =================================================
        # NAVIGATION
        # =================================================

        st.markdown("### Navigation")

        st.page_link(
            "app.py",
            label="Accueil",
            icon="🏠",
            use_container_width=True,
        )

        st.page_link(
            "pages/1_Synthese_Executive.py",
            label="Synthèse Exécutive",
            icon="📊",
            use_container_width=True,
        )

        st.page_link(
            "pages/2_Maturite_Performance.py",
            label="Maturité & Performance",
            icon="📈",
            use_container_width=True,
        )

        st.page_link(
            "pages/3_Findings_Actions.py",
            label="Findings & Actions",
            icon="⚠️",
            use_container_width=True,
        )

        st.page_link(
            "pages/4_Detail_Compte.py",
            label="Détail Compte",
            icon="🔎",
            use_container_width=True,
        )
        st.page_link(
            "pages/5_Monitoring_Escalades.py",
            label="Monitoring & Escalades",
            icon="🚨",
        )

        st.divider()

        # =================================================
        # REFRESH
        # =================================================

        st.markdown("### Données")

        if st.button(
            "🔄 Actualiser les données",
            use_container_width=True,
            type="primary",
        ):

            st.cache_data.clear()

            st.toast(
                "Données actualisées",
                icon="✅",
            )

            st.rerun()

        st.caption(
            "Les dashboards utilisent les marts "
            "Analytics PostgreSQL / dbt."
        )


def render_header(
    title: str,
    subtitle: str,
):
    html = (
        f'<div class="qip-header">'
        f'<div class="qip-header-title">{title}</div>'
        f'<div class="qip-header-subtitle">{subtitle}</div>'
        f'</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def kpi_card(
    title,
    value,
    accent_color,
    soft_color,
):
    html = (
        f'<div class="kpi-card" '
        f'style="border-top:6px solid {accent_color};'
        f'background:linear-gradient(135deg,#FFFFFF 0%,{soft_color} 100%);">'
        f'<div class="kpi-title">{title}</div>'
        f'<div class="kpi-value" style="color:{accent_color};">{value}</div>'
        f'</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )