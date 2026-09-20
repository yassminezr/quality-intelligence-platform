from pathlib import Path

from src.ingestion.audit_status_extractor import (
    extract_audit_statuses,
)


excel_file = Path(
    "data/incoming"
) / "QHC_ISO9001_Audits & consolidation FY27 (1).xlsx"


statuses = extract_audit_statuses(
    excel_file
)


print(
    statuses.to_string(
        index=False
    )
)


print(
    "\nNombre de comptes :",
    len(statuses),
)


print(
    "\nRépartition :"
)

print(
    statuses[
        "validated_status"
    ].value_counts()
)