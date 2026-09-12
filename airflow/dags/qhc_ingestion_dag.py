from __future__ import annotations

from datetime import datetime
from pathlib import Path

from airflow import DAG
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
from src.quality.run_data_quality import (
    execute_data_quality,
)


def run_qhc_ingestion():
    incoming_file = find_incoming_excel(
        INCOMING_DIR
    )

    batch_id = run_ingestion(
        source_file=incoming_file,
        campaign=CURRENT_CAMPAIGN,
    )

    return batch_id


def run_qhc_data_quality(**context):
    batch_id = context["ti"].xcom_pull(
        task_ids="ingest_qhc_file"
    )

    if batch_id is None:
        print(
            "No new batch created. "
            "Data Quality skipped."
        )
        return

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

    report, gate_result = execute_data_quality(
        input_file=standardized_file,
        output_dir=quality_dir,
    )

    print(
        "DQ total issues:",
        report.total_issues,
    )

    print(
        "DQ gate:",
        "CONTINUE"
        if gate_result.can_continue
        else "BLOCK",
    )

    if not gate_result.can_continue:
        raise ValueError(
            gate_result.reason
        )


with DAG(
    dag_id="qhc_ingestion_pipeline",
    description=(
        "QHC ingestion and Data Quality pipeline"
    ),
    start_date=datetime(2026, 9, 1),
    schedule=None,
    catchup=False,
    tags=[
        "qhc",
        "quality",
        "ingestion",
        "data-quality",
    ],
) as dag:

    ingest_qhc_file = PythonOperator(
        task_id="ingest_qhc_file",
        python_callable=run_qhc_ingestion,
    )

    run_data_quality_task = PythonOperator(
        task_id="run_data_quality",
        python_callable=run_qhc_data_quality,
    )

    ingest_qhc_file >> run_data_quality_task