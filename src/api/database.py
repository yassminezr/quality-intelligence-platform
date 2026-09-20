from __future__ import annotations

from typing import Any

from src.common.database import get_postgres_connection


def fetch_all(
    query: str,
    params: tuple[Any, ...] | None = None,
) -> list[dict]:
    """
    Exécute une requête SELECT et retourne
    toutes les lignes sous forme de dictionnaires.
    """

    with get_postgres_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                query,
                params or (),
            )

            rows = cursor.fetchall()

            if cursor.description is None:
                return []

            columns = [
                column.name
                for column in cursor.description
            ]

    return [
        dict(zip(columns, row))
        for row in rows
    ]


def fetch_one(
    query: str,
    params: tuple[Any, ...] | None = None,
) -> dict | None:
    """
    Exécute une requête SELECT et retourne
    une seule ligne sous forme de dictionnaire.
    """

    with get_postgres_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                query,
                params or (),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            columns = [
                column.name
                for column in cursor.description
            ]

    return dict(
        zip(
            columns,
            row,
        )
    )