from __future__ import annotations

import os

import psycopg


def get_postgres_connection():
    """
    Retourne une connexion PostgreSQL.

    Les valeurs par défaut correspondent
    à l'environnement local Docker.
    """

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
    )