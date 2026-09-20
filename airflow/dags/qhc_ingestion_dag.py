from __future__ import annotations

from datetime import datetime
import subprocess

from airflow import DAG
from airflow.exceptions import AirflowSkipException
from airflow.operators.python import PythonOperator

from src.common.config import (
    CURRENT_CAMPAIGN,
    INCOMING_DIR,
    STANDARDIZED_DIR,
)

from src.ingestion.incoming_file import (
    find_incoming_excel,
)

from src.ingestion.run_ingestion import (
    run_ingestion,
)

from src.ingestion.postgres_loader import (
    load_standardized_batch,
)

from src.ingestion.postgres_audit_status_loader import (
    load_audit_status_snapshot,
)

from src.quality.run_data_quality import (
    execute_data_quality,
)

from src.quality.postgres_dq_loader import (
    load_dq_issues,
)

from src.modeling.load_audit_core import (
    load_audit_core,
)

from src.modeling.load_iso_reference import (
    load_iso_reference,
)

from src.modeling.load_evaluation_core import (
    load_evaluation_core,
)

from src.modeling.load_audit_validations import (
    load_audit_validations,
)


# =====================================================
# Helper — Batch ID
# =====================================================

def get_batch_id(context):
    """
    Récupère le batch_id créé
    par la tâche d'ingestion.
    """

    batch_id = context["ti"].xcom_pull(
        task_ids="ingest_qhc_file"
    )

    if batch_id is None:
        raise AirflowSkipException(
            "No new ingestion batch."
        )

    return batch_id


# =====================================================
# Helper — dbt
# =====================================================

def run_dbt_command(command: str):
    """
    Exécute une commande dbt dans le projet analytics.
    """

    project_dir = (
        "/opt/airflow/project/analytics/qip_analytics"
    )

    result = subprocess.run(
        [
            "dbt",
            command,
            "--project-dir",
            project_dir,
            "--profiles-dir",
            project_dir,
        ],
        capture_output=True,
        text=True,
    )

    print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(
            f"dbt {command} failed with exit code "
            f"{result.returncode}"
        )


# =====================================================
# Task 1 — Ingestion
# =====================================================

def run_qhc_ingestion():

    incoming_file = find_incoming_excel(
        INCOMING_DIR
    )

    batch_id = run_ingestion(
        source_file=incoming_file,
        campaign=CURRENT_CAMPAIGN,
    )

    if batch_id is None:
        raise AirflowSkipException(
            "File already ingested. "
            "Pipeline skipped."
        )

    print(
        "Created batch:",
        batch_id,
    )

    return batch_id


# =====================================================
# Task 2 — Data Quality
# =====================================================

def run_qhc_data_quality(**context):

    batch_id = get_batch_id(
        context
    )

    standardized_file = (
        STANDARDIZED_DIR
        / CURRENT_CAMPAIGN
        / batch_id
        / "standardized_audits.csv"
    )

    quality_dir = (
        STANDARDIZED_DIR
        / CURRENT_CAMPAIGN
        / batch_id
        / "quality"
    )

    report, gate_result = (
        execute_data_quality(
            input_file=standardized_file,
            output_dir=quality_dir,
        )
    )

    print(
        "DQ total issues:",
        report.total_issues,
    )

    print(
        "DQ errors:",
        report.error_count,
    )

    print(
        "DQ blocking:",
        report.blocking_count,
    )

    print(
        "DQ Gate:",
        (
            "CONTINUE"
            if gate_result.can_continue
            else "BLOCK"
        ),
    )

    if not gate_result.can_continue:
        raise ValueError(
            gate_result.reason
        )


# =====================================================
# Task 3 — PostgreSQL Staging
# =====================================================

def load_postgres_staging(**context):

    batch_id = get_batch_id(
        context
    )

    standardized_file = (
        STANDARDIZED_DIR
        / CURRENT_CAMPAIGN
        / batch_id
        / "standardized_audits.csv"
    )

    loaded_rows = load_standardized_batch(
        csv_path=standardized_file,
        batch_id=batch_id,
    )

    print(
        "Staging rows loaded:",
        loaded_rows,
    )


# =====================================================
# Task 4 — PostgreSQL DQ Issues
# =====================================================

def load_postgres_dq(**context):

    batch_id = get_batch_id(
        context
    )

    dq_file = (
        STANDARDIZED_DIR
        / CURRENT_CAMPAIGN
        / batch_id
        / "quality"
        / "dq_issues.csv"
    )

    loaded_rows = load_dq_issues(
        csv_path=dq_file,
        batch_id=batch_id,
    )

    print(
        "DQ issues loaded:",
        loaded_rows,
    )


# =====================================================
# Task 5 — Official Audit Status Snapshot
# =====================================================

def load_audit_status_snapshot_task(**context):
    """
    Extrait les statuts officiels depuis la feuille
    DASHBOARD AUDITS et les charge dans PostgreSQL staging.
    """

    batch_id = get_batch_id(
        context
    )

    incoming_file = find_incoming_excel(
        INCOMING_DIR
    )

    loaded_statuses = load_audit_status_snapshot(
        excel_file=incoming_file,
        batch_id=batch_id,
    )

    print(
        "Official audit statuses loaded:",
        loaded_statuses,
    )


# =====================================================
# Task 6 — Account / Campaign / Audit
# =====================================================

def load_core_audits(**context):

    batch_id = get_batch_id(
        context
    )

    result = load_audit_core(
        batch_id=batch_id
    )

    print(
        "Accounts:",
        result["accounts"],
    )

    print(
        "Audits:",
        result["audits"],
    )


# =====================================================
# Task 7 — ISO Reference
# =====================================================

def load_core_iso(**context):

    batch_id = get_batch_id(
        context
    )

    result = load_iso_reference(
        batch_id=batch_id
    )

    print(
        "ISO clauses:",
        result["clauses"],
    )

    print(
        "ISO controls:",
        result["controls"],
    )


# =====================================================
# Task 8 — Evaluations / Findings / Actions
# =====================================================

def load_core_evaluations(**context):

    batch_id = get_batch_id(
        context
    )

    result = load_evaluation_core(
        batch_id=batch_id
    )

    print(
        "Evaluations:",
        result["evaluations"],
    )

    print(
        "Findings:",
        result["findings"],
    )

    print(
        "Corrective actions:",
        result["actions"],
    )

    print(
        "Evaluation changes:",
        result["evaluation_changes"],
    )

    print(
        "Action changes:",
        result["action_changes"],
    )

    print(
        "Action status changes:",
        result["action_status_changes"],
    )


# =====================================================
# Task 9 — Official Audit Validations
# =====================================================

def load_core_validations(**context):
    """
    Met à jour le statut officiel courant des audits
    depuis staging.audit_status_snapshot.

    DASHBOARD AUDITS est désormais la source officielle.
    """

    batch_id = get_batch_id(
        context
    )

    result = load_audit_validations(
        batch_id=batch_id
    )

    print(
        "Official statuses processed:",
        result["total"],
    )

    print(
        "Official statuses updated:",
        result["updated"],
    )

    print(
        "Official statuses unchanged:",
        result["unchanged"],
    )


# =====================================================
# Task 10 — dbt Models
# =====================================================

def run_dbt_models():

    run_dbt_command("run")


# =====================================================
# Task 11 — dbt Tests
# =====================================================

def run_dbt_tests():

    run_dbt_command("test")


# =====================================================
# DAG
# =====================================================

with DAG(
    dag_id="qhc_ingestion_pipeline",

    description=(
        "End-to-end QHC ingestion, "
        "Data Quality, PostgreSQL loading, "
        "official audit status synchronization "
        "and dbt transformation pipeline"
    ),

    start_date=datetime(
        2026,
        9,
        1,
    ),

    schedule=None,

    catchup=False,

    tags=[
        "qhc",
        "quality",
        "postgresql",
        "data-quality",
        "audit-status",
        "dbt",
    ],

) as dag:

    # -------------------------------------------------
    # Task 1 — Ingestion
    # -------------------------------------------------

    ingest_qhc_file = PythonOperator(
        task_id="ingest_qhc_file",
        python_callable=run_qhc_ingestion,
    )

    # -------------------------------------------------
    # Task 2 — Data Quality
    # -------------------------------------------------

    run_data_quality_task = PythonOperator(
        task_id="run_data_quality",
        python_callable=run_qhc_data_quality,
    )

    # -------------------------------------------------
    # Task 3 — PostgreSQL Staging
    # -------------------------------------------------

    load_staging_task = PythonOperator(
        task_id="load_postgres_staging",
        python_callable=load_postgres_staging,
    )

    # -------------------------------------------------
    # Task 4 — PostgreSQL DQ
    # -------------------------------------------------

    load_dq_task = PythonOperator(
        task_id="load_postgres_dq",
        python_callable=load_postgres_dq,
    )

    # -------------------------------------------------
    # Task 5 — Official Audit Status Snapshot
    # -------------------------------------------------

    load_status_snapshot_task = PythonOperator(
        task_id="load_audit_status_snapshot",
        python_callable=load_audit_status_snapshot_task,
    )

    # -------------------------------------------------
    # Task 6 — Core Audits
    # -------------------------------------------------

    load_audits_task = PythonOperator(
        task_id="load_core_audits",
        python_callable=load_core_audits,
    )

    # -------------------------------------------------
    # Task 7 — ISO Reference
    # -------------------------------------------------

    load_iso_task = PythonOperator(
        task_id="load_core_iso",
        python_callable=load_core_iso,
    )

    # -------------------------------------------------
    # Task 8 — Evaluations
    # -------------------------------------------------

    load_evaluations_task = PythonOperator(
        task_id="load_core_evaluations",
        python_callable=load_core_evaluations,
    )

    # -------------------------------------------------
    # Task 9 — Official Validations
    # -------------------------------------------------

    load_validations_task = PythonOperator(
        task_id="load_core_validations",
        python_callable=load_core_validations,
    )

    # -------------------------------------------------
    # Task 10 — dbt Run
    # -------------------------------------------------

    dbt_models_task = PythonOperator(
        task_id="run_dbt_models",
        python_callable=run_dbt_models,
    )

    # -------------------------------------------------
    # Task 11 — dbt Test
    # -------------------------------------------------

    dbt_tests_task = PythonOperator(
        task_id="run_dbt_tests",
        python_callable=run_dbt_tests,
    )

    # =================================================
    # Pipeline Dependencies
    # =================================================

    (
        ingest_qhc_file
        >> run_data_quality_task
        >> load_staging_task
        >> load_dq_task
        >> load_status_snapshot_task
        >> load_audits_task
        >> load_iso_task
        >> load_evaluations_task
        >> load_validations_task
        >> dbt_models_task
        >> dbt_tests_task
    )