from __future__ import annotations

import os

import pandas as pd
import psycopg


def get_connection():
    return psycopg.connect(
        host=os.getenv(
            "POSTGRES_HOST",
            "localhost",
        ),
        port=os.getenv(
            "POSTGRES_PORT",
            "5432",
        ),
        dbname=os.getenv(
            "POSTGRES_DB",
            "quality_intelligence",
        ),
        user=os.getenv(
            "POSTGRES_USER",
            "qip_user",
        ),
        password=os.getenv(
            "POSTGRES_PASSWORD",
            "qip_password",
        ),
        connect_timeout=5,
    )


def query_dataframe(query: str) -> pd.DataFrame:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)

            rows = cur.fetchall()

            columns = [
                description.name
                for description in cur.description
            ]

    return pd.DataFrame(
        rows,
        columns=columns,
    )