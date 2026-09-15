from __future__ import annotations

import argparse
from pathlib import Path

from src.ingestion.postgres_loader import (
    load_standardized_batch,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Load a standardized audit batch "
            "into PostgreSQL staging."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to standardized_audits.csv",
    )

    parser.add_argument(
        "--batch-id",
        required=True,
        help="Ingestion batch UUID",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    loaded_rows = load_standardized_batch(
        csv_path=args.input,
        batch_id=args.batch_id,
    )

    print(
        f"Successfully loaded "
        f"{loaded_rows} rows "
        f"into PostgreSQL staging."
    )


if __name__ == "__main__":
    main()