from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

INCOMING_DIR = DATA_DIR / "incoming"
RAW_DIR = DATA_DIR / "raw"
STANDARDIZED_DIR = DATA_DIR / "standardized"
PROFILING_DIR = DATA_DIR / "profiling"
REFERENCE_DIR = DATA_DIR / "reference"

CURRENT_CAMPAIGN = "FY27"


def ensure_directories() -> None:
    """
    Crée les dossiers nécessaires s'ils n'existent pas.
    """

    directories = [
        INCOMING_DIR,
        RAW_DIR,
        STANDARDIZED_DIR,
        PROFILING_DIR,
        REFERENCE_DIR,
    ]

    for directory in directories:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )