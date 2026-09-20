import streamlit as st

from data.database import query_dataframe


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


@st.cache_data(ttl=300)
def load_findings():
    return query_dataframe(
        """
        SELECT *
        FROM analytics.mart_findings
        ORDER BY account_name, clause_iso
        """
    )


@st.cache_data(ttl=300)
def load_corrective_actions():
    return query_dataframe(
        """
        SELECT *
        FROM analytics.mart_corrective_actions
        ORDER BY account_name, age_jours DESC NULLS LAST
        """
    )


@st.cache_data(ttl=300)
def load_maturity_distribution():
    return query_dataframe(
        """
        SELECT *
        FROM analytics.mart_maturity_distribution
        ORDER BY account_name
        """
    )