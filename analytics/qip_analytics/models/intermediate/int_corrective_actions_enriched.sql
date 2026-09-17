with actions as (

    select *
    from {{ ref('stg_corrective_actions') }}

),

findings as (

    select *
    from {{ ref('int_findings_enriched') }}

)

select

    a.action_id,

    f.finding_id,
    f.evaluation_id,
    f.audit_id,

    f.account_id,
    f.account_name,

    f.campaign_id,
    f.campaign_name,

    f.clause_id,
    f.clause_iso,

    f.categorie_finding,

    a.action_text,
    a.responsable,

    a.date_debut,
    a.date_cloture,

    a.statut,

    case
        when a.date_debut is null then null

        when lower(coalesce(a.statut, '')) = 'clôturé'
             and a.date_cloture is not null
            then a.date_cloture - a.date_debut

        else current_date - a.date_debut
    end as age_jours,

    case

        when a.date_debut is null
            then null

        when (
            case
                when lower(coalesce(a.statut, '')) = 'clôturé'
                     and a.date_cloture is not null
                    then a.date_cloture - a.date_debut

                else current_date - a.date_debut
            end
        ) <= 30
            then 'Normal'

        when (
            case
                when lower(coalesce(a.statut, '')) = 'clôturé'
                     and a.date_cloture is not null
                    then a.date_cloture - a.date_debut

                else current_date - a.date_debut
            end
        ) <= 60
            then 'Alerte'

        when (
            case
                when lower(coalesce(a.statut, '')) = 'clôturé'
                     and a.date_cloture is not null
                    then a.date_cloture - a.date_debut

                else current_date - a.date_debut
            end
        ) <= 90
            then 'Critique'

        else 'Escalade management'

    end as indicateur_age,

    a.created_at,
    a.updated_at

from actions a

join findings f
    on a.finding_id = f.finding_id