from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.monitoring.run_monitoring import run_monitoring


with DAG(
    dag_id="corrective_action_monitoring",
    description="Monitoring des actions correctives et escalades QIP",
    start_date=datetime(2026, 9, 20),
    schedule="@daily",
    catchup=False,
    tags=["qip", "monitoring", "corrective-actions"],
) as dag:

    run_corrective_action_monitoring = PythonOperator(
        task_id="run_corrective_action_monitoring",
        python_callable=run_monitoring,
    )