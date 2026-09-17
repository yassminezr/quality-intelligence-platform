select

    action_id,

    finding_id,
    evaluation_id,
    audit_id,

    account_id,
    account_name,

    campaign_id,
    campaign_name,

    clause_id,
    clause_iso,

    categorie_finding,

    action_text,
    responsable,

    date_debut,
    date_cloture,

    statut,

    age_jours,
    indicateur_age,

    case
        when lower(
            coalesce(statut, '')
        ) = 'clôturé'
            then true

        else false
    end as is_closed,

    case
        when lower(
            coalesce(statut, '')
        ) = 'clôturé'
            then false

        else true
    end as is_open,

    case
        when indicateur_age in (
            'Critique',
            'Escalade management'
        )
            then true

        else false
    end as requires_attention,

    created_at,
    updated_at

from {{ ref('int_corrective_actions_enriched') }}