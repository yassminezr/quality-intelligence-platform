from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


VALID_STATUSES = {
    "non_audite",
    "en_cours",
    "audite",
    "a_valider",
}


def load_completion_profile(
    path: Path,
) -> dict:

    if not path.exists():
        raise FileNotFoundError(
            f"Completion profile not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_validations(
    path: Path,
) -> pd.DataFrame:

    if not path.exists():
        raise FileNotFoundError(
            f"Validation file not found: {path}"
        )

    return pd.read_csv(
        path,
        encoding="utf-8-sig",
    )


def propose_status(
    evaluated_controls: int,
    account_scope_controls: int,
) -> tuple[str, str]:
    """
    Produit une proposition automatique de statut.

    Règle provisoire :
    - 0 %        -> non_audite
    - >0 et <65% -> en_cours
    - >65%       -> audite
    - 65% exact  -> a_valider

    IMPORTANT :
    Cette règle sert uniquement d'aide à la décision.
    Le statut validé par l'équipe Qualité reste prioritaire.
    """

    if account_scope_controls == 0:
        return (
            "a_valider",
            "Aucun contrôle applicable identifié."
        )

    completion_rate = (
        evaluated_controls
        / account_scope_controls
        * 100
    )

    if completion_rate == 0:
        return (
            "non_audite",
            "Aucun contrôle applicable évalué."
        )

    if 0 < completion_rate < 65:
        return (
            "en_cours",
            "Le taux de complétude est supérieur à 0 % "
            "et inférieur à 65 %."
        )

    if completion_rate > 65:
        return (
            "audite",
            "Le taux de complétude est supérieur à 65 %."
        )

    return (
        "a_valider",
        "Le taux de complétude est exactement de 65 %. "
        "La règle métier ne définit pas encore ce cas."
    )

def validate_manual_statuses(
    validations: pd.DataFrame,
) -> None:

    invalid_rows = validations[
        ~validations["statut_valide"].isin(
            VALID_STATUSES
        )
        & validations["statut_valide"].notna()
    ]

    if not invalid_rows.empty:
        raise ValueError(
            "Invalid validated audit status detected."
        )


def build_validation_lookup(
    validations: pd.DataFrame,
) -> dict:

    lookup = {}

    for _, row in validations.iterrows():

        account = row["source_sheet"]

        lookup[account] = {
            "statut_valide": (
                row["statut_valide"]
                if pd.notna(row["statut_valide"])
                else None
            ),
            "date_validation": (
                row["date_validation"]
                if pd.notna(row["date_validation"])
                else None
            ),
            "valide_par": (
                row["valide_par"]
                if pd.notna(row["valide_par"])
                else None
            ),
        }

    return lookup


def build_report(
    completion_profile: dict,
    validations: pd.DataFrame,
) -> dict:

    validate_manual_statuses(validations)

    validation_lookup = (
        build_validation_lookup(
            validations
        )
    )

    accounts = []

    for account in completion_profile["accounts"]:

        account_name = account["source_sheet"]

        proposed_status, reason = propose_status(
            evaluated_controls=(
                account["evaluated_controls"]
            ),
            account_scope_controls=(
                account["account_scope_controls"]
            ),
        )

        manual_validation = (
            validation_lookup.get(
                account_name,
                {},
            )
        )

        validated_status = (
            manual_validation.get(
                "statut_valide"
            )
        )

        official_status = (
            validated_status
            if validated_status
            else proposed_status
        )

        accounts.append(
            {
                "source_sheet": account_name,

                "completion_rate":
                    account["completion_rate"],

                "statut_propose":
                    proposed_status,

                "raison_proposition":
                    reason,

                "statut_valide":
                    validated_status,

                "date_validation":
                    manual_validation.get(
                        "date_validation"
                    ),

                "valide_par":
                    manual_validation.get(
                        "valide_par"
                    ),

                "statut_officiel":
                    official_status,

                "validation_requise":
                    validated_status is None,
            }
        )

    return {
        "rule_version": "v0.1",
        "rule_is_official": False,
        "accounts": accounts,
    }


def save_report(
    report: dict,
    output_path: Path,
) -> None:

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )


def print_report(report: dict) -> None:

    print(
        "Audit status proposal completed.\n"
    )

    for account in report["accounts"]:

        print(
            f"{account['source_sheet']}: "
            f"proposed={account['statut_propose']} | "
            f"validated={account['statut_valide']} | "
            f"official={account['statut_officiel']} | "
            f"completion={account['completion_rate']}%"
        )


def parse_arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--completion",
        default=Path(
            "data/profiling/"
            "audit_completion_profile.json"
        ),
        type=Path,
    )

    parser.add_argument(
        "--validations",
        default=Path(
            "data/reference/"
            "account_status_validations.csv"
        ),
        type=Path,
    )

    parser.add_argument(
        "--output",
        default=Path(
            "data/profiling/"
            "audit_status_profile.json"
        ),
        type=Path,
    )

    return parser.parse_args()


def main():

    args = parse_arguments()

    completion_profile = (
        load_completion_profile(
            args.completion
        )
    )

    validations = load_validations(
        args.validations
    )

    report = build_report(
        completion_profile,
        validations,
    )

    save_report(
        report,
        args.output,
    )

    print_report(report)

    print(
        f"\nReport saved to: {args.output}"
    )


if __name__ == "__main__":
    main()