select

    finding_id,

    evaluation_id,
    audit_id,

    account_id,
    account_name,

    campaign_id,
    campaign_name,

    clause_id,
    clause_iso,
    intitule_iso,

    control_id,
    libelle_terrain,

    categorie_finding,

    score_maturite,
    niveau_maturite,

    constat_auditeur,

    case
        when categorie_finding
            not in (
                'Bonne Pratique',
                'NA'
            )
            then true

        else false
    end as is_counted_in_total_findings,

    created_at

from {{ ref('int_findings_enriched') }}