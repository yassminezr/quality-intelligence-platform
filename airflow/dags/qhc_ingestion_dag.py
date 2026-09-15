from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.exceptions import (
    AirflowSkipException,
)
from airflow.operators.python import (
    PythonOperator,
)

from src.common.config import (
    CURRENT_CAMPAIGN,
    INCOMING_DIR,
    STANDARDIZED_DIR,
    REFERENCE_DIR,
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
# Helper
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
# Task 5 — Account / Campaign / Audit
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
# Task 6 — ISO Reference
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
# Task 7 — Evaluations / Findings / Actions
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
        result[
            "action_status_changes"
        ],
    )


# =====================================================
# Task 8 — Official Audit Validations
# =====================================================

def load_core_validations():

    validation_file = (
        REFERENCE_DIR
        / "account_status_validations.csv"
    )

    result = load_audit_validations(
        csv_path=validation_file,
        campaign_name=CURRENT_CAMPAIGN,
    )

    print(
        "Validated audits updated:",
        result["updated"],
    )

    print(
        "Validation history created:",
        result["history_created"],
    )

    print(
        "Unchanged validations:",
        result["unchanged"],
    )


# =====================================================
# DAG
# =====================================================

with DAG(
    dag_id="qhc_ingestion_pipeline",

    description=(
        "End-to-end QHC ingestion, "
        "Data Quality and PostgreSQL "
        "loading pipeline"
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
    ],

) as dag:

    ingest_qhc_file = PythonOperator(
        task_id="ingest_qhc_file",
        python_callable=run_qhc_ingestion,
    )

    run_data_quality_task = (
        PythonOperator(
            task_id="run_data_quality",
            python_callable=(
                run_qhc_data_quality
            ),
        )
    )

    load_staging_task = PythonOperator(
        task_id="load_postgres_staging",
        python_callable=(
            load_postgres_staging
        ),
    )

    load_dq_task = PythonOperator(
        task_id="load_postgres_dq",
        python_callable=(
            load_postgres_dq
        ),
    )

    load_audits_task = PythonOperator(
        task_id="load_core_audits",
        python_callable=(
            load_core_audits
        ),
    )

    load_iso_task = PythonOperator(
        task_id="load_core_iso",
        python_callable=(
            load_core_iso
        ),
    )

    load_evaluations_task = (
        PythonOperator(
            task_id="load_core_evaluations",
            python_callable=(
                load_core_evaluations
            ),
        )
    )

    load_validations_task = (
        PythonOperator(
            task_id="load_core_validations",
            python_callable=(
                load_core_validations
            ),
        )
    )

    (
        ingest_qhc_file
        >> run_data_quality_task
        >> load_staging_task
        >> load_dq_task
        >> load_audits_task
        >> load_iso_task
        >> load_evaluations_task
        >> load_validations_task
    )