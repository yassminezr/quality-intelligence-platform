import pandas as pd
import plotly.express as px
import streamlit as st

from data.loaders import (
    load_action_monitoring_history,
    load_monitoring_runs,
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
    SOFT_BLUE,
    SOFT_SKY,
    SOFT_GOLD,
    SOFT_RED,
)


# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Monitoring & Escalades | QIP",
    page_icon="🚨",
    layout="wide",
)

apply_global_theme()
render_sidebar()

render_header(
    "Monitoring & Escalades",
    "Suivi du moteur de monitoring et des changements de niveau des actions correctives",
)


# =====================================================
# DATA
# =====================================================

runs = load_monitoring_runs()
history = load_action_monitoring_history()


# =====================================================
# KPI DERNIER RUN
# =====================================================

st.markdown(
    '<div class="section-title">'
    'Dernière exécution'
    '</div>',
    unsafe_allow_html=True,
)


if runs.empty:

    st.info(
        "Aucune exécution de monitoring disponible."
    )

else:

    latest_run = runs.iloc[0]

    status = str(
        latest_run["status"]
    ).upper()

    actions_evaluated = int(
        latest_run["actions_evaluated"] or 0
    )

    events_detected = int(
        latest_run["events_detected"] or 0
    )

    emails_sent = int(
        latest_run["emails_sent"] or 0
    )

    emails_failed = int(
        latest_run["emails_failed"] or 0
    )


    c1, c2, c3, c4, c5 = st.columns(5)


    with c1:

        status_color = (
            ROYAL
            if status == "SUCCESS"
            else RED
        )

        status_soft = (
            SOFT_SKY
            if status == "SUCCESS"
            else SOFT_RED
        )

        kpi_card(
            "Dernier statut",
            status,
            status_color,
            status_soft,
        )


    with c2:

        kpi_card(
            "Actions évaluées",
            actions_evaluated,
            ROYAL,
            SOFT_BLUE,
        )


    with c3:

        kpi_card(
            "Événements détectés",
            events_detected,
            GOLD,
            SOFT_GOLD,
        )


    with c4:

        kpi_card(
            "Emails envoyés",
            emails_sent,
            ROYAL,
            SOFT_SKY,
        )


    with c5:

        kpi_card(
            "Échecs email",
            emails_failed,
            RED,
            SOFT_RED,
        )


# =====================================================
# HISTORIQUE RUNS
# =====================================================

st.markdown(
    '<div class="section-title">'
    'Historique des exécutions'
    '</div>',
    unsafe_allow_html=True,
)


if runs.empty:

    st.info(
        "Aucun run disponible."
    )

else:

    runs_display = runs[
        [
            "run_id",
            "started_at",
            "finished_at",
            "status",
            "actions_evaluated",
            "events_detected",
            "messages_prepared",
            "emails_sent",
            "emails_failed",
            "duration_seconds",
        ]
    ].head(20).copy()


    runs_display = runs_display.rename(
        columns={
            "run_id": "Run ID",
            "started_at": "Début",
            "finished_at": "Fin",
            "status": "Statut",
            "actions_evaluated": "Actions évaluées",
            "events_detected": "Événements",
            "messages_prepared": "Messages préparés",
            "emails_sent": "Emails envoyés",
            "emails_failed": "Échecs email",
            "duration_seconds": "Durée (s)",
        }
    )


    st.dataframe(
        runs_display,
        use_container_width=True,
        hide_index=True,
    )


# =====================================================
# CHANGEMENTS DE NIVEAU
# =====================================================

st.markdown(
    '<div class="section-title">'
    'Changements de niveau'
    '</div>',
    unsafe_allow_html=True,
)


if history.empty:

    st.info(
        "Aucun changement de niveau enregistré."
    )

else:

    # -------------------------------------------------
    # Répartition des niveaux
    # -------------------------------------------------

    level_counts = (
        history[
            "niveau_escalade"
        ]
        .fillna("Non renseigné")
        .value_counts()
        .reset_index()
    )

    level_counts.columns = [
        "Niveau",
        "Nombre",
    ]


    level_colors = {
        "Normal": SKY,
        "Alerte": GOLD,
        "Critique": PEACH,
        "Escalade management": RED,
        "Non renseigné": "#7B8794",
    }


    fig = px.bar(
        level_counts,
        x="Niveau",
        y="Nombre",
        color="Niveau",
        text="Nombre",
        color_discrete_map=level_colors,
    )


    fig.update_traces(
        textposition="outside",
    )


    fig.update_layout(
        showlegend=False,
        xaxis_title=None,
        yaxis_title="Nombre de changements",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFF9F2",
        font=dict(
            color=MIDNIGHT_BLUE
        ),
    )


    st.plotly_chart(
        fig,
        use_container_width=True,
    )


    # -------------------------------------------------
    # Historique détaillé
    # -------------------------------------------------

    history_display = history[
        [
            "action_id",
            "age_jours",
            "niveau_escalade",
            "monitored_at",
        ]
    ].head(50).copy()


    history_display = history_display.rename(
        columns={
            "action_id": "Action ID",
            "age_jours": "Âge (jours)",
            "niveau_escalade": "Niveau",
            "monitored_at": "Détecté le",
        }
    )


    st.dataframe(
        history_display,
        use_container_width=True,
        hide_index=True,
    )