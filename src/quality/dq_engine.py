from __future__ import annotations

import pandas as pd

from src.quality.completeness_checks import (
    check_finding_required_after_evaluation,
)
from src.quality.consistency_checks import (
    check_action_requires_valid_finding,
    check_closed_action_has_closure_date,
    check_na_without_corrective_action,
)
from src.quality.date_checks import (
    check_closure_before_start,
    check_invalid_dates,
)
from src.quality.domain_checks import (
    check_finding_category_domain,
    check_score_domain,
)
from src.quality.dq_models import (
    DQIssue,
    DQReport,
)
from src.quality.schema_checks import (
    check_required_columns,
)


def run_data_quality(
    df: pd.DataFrame,
) -> DQReport:
    """
    Exécute l'ensemble des règles Data Quality
    sur le dataset standardisé.
    """

    issues: list[DQIssue] = []

    # 1. Schema
    issues.extend(
        check_required_columns(df)
    )

    # 2. Domain
    issues.extend(
        check_score_domain(df)
    )

    issues.extend(
        check_finding_category_domain(df)
    )

    # 3. Conditional completeness
    issues.extend(
        check_finding_required_after_evaluation(
            df
        )
    )

    # 4. Business consistency
    issues.extend(
        check_na_without_corrective_action(
            df
        )
    )

    issues.extend(
        check_action_requires_valid_finding(
            df
        )
    )

    issues.extend(
        check_closed_action_has_closure_date(
            df
        )
    )

    # 5. Dates
    issues.extend(
        check_invalid_dates(df)
    )

    issues.extend(
        check_closure_before_start(
            df
        )
    )

    return DQReport(
        issues=issues
    )