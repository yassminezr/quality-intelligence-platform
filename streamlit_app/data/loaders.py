import streamlit as st

from data.database import query_dataframe


# =====================================================
# AUDITS
# =====================================================

@st.cache_data(ttl=300)
def load_audit_overview():
    return query_dataframe(
        """
        SELECT *
        FROM analytics.mart_audit_overview
        ORDER BY account_name
        """
    )


@st.cache_data(ttl=300)
def load_account_clause_detail():
    return query_dataframe(
        """
        SELECT *
        FROM analytics.mart_account_clause_detail
        ORDER BY account_name, clause_iso
        """
    )


# =====================================================
# FINDINGS
# =====================================================

@st.cache_data(ttl=300)
def load_findings():
    return query_dataframe(
        """
        SELECT *
        FROM analytics.mart_findings
        ORDER BY account_name, clause_iso
        """
    )


# =====================================================
# ACTIONS CORRECTIVES
# =====================================================

@st.cache_data(ttl=300)
def load_corrective_actions():
    return query_dataframe(
        """
        SELECT *
        FROM analytics.mart_corrective_actions
        ORDER BY account_name, age_jours DESC NULLS LAST
        """
    )


# =====================================================
# MATURITE
# =====================================================

@st.cache_data(ttl=300)
def load_maturity_distribution():
    return query_dataframe(
        """
        SELECT *
        FROM analytics.mart_maturity_distribution
        ORDER BY account_name
        """
    )


# =====================================================
# MONITORING RUNS
# =====================================================

@st.cache_data(ttl=300)
def load_monitoring_runs():
    return query_dataframe(
        """
        SELECT
            run_id,
            started_at,
            finished_at,
            status,
            actions_evaluated,
            events_detected,
            messages_prepared,
            emails_sent,
            emails_failed,
            duration_seconds
        FROM analytics.mart_monitoring_runs
        ORDER BY started_at DESC
        """
    )


# =====================================================
# MONITORING HISTORY
# =====================================================

@st.cache_data(ttl=300)
def load_action_monitoring_history():
    return query_dataframe(
        """
        SELECT
            monitoring_log_id,
            action_id,
            age_jours,
            niveau_escalade,
            monitored_at
        FROM analytics.mart_action_monitoring_history
        ORDER BY monitored_at DESC
        """
    )