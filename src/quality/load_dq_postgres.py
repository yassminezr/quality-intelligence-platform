from __future__ import annotations

import argparse
from pathlib import Path

from src.quality.postgres_dq_loader import (
    load_dq_issues,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Load Data Quality issues "
            "into PostgreSQL."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to dq_issues.csv",
    )

    parser.add_argument(
        "--batch-id",
        required=True,
        help="Ingestion batch UUID",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    loaded_rows = load_dq_issues(
        csv_path=args.input,
        batch_id=args.batch_id,
    )

    print(
        f"Successfully loaded "
        f"{loaded_rows} Data Quality issues "
        f"into PostgreSQL."
    )


if __name__ == "__main__":
    main()