with audits as (

    select *
    from {{ ref('stg_audits') }}

),

accounts as (

    select *
    from {{ ref('stg_accounts') }}

),

campaigns as (

    select *
    from {{ ref('stg_campaigns') }}

),

evaluations as (

    select *
    from {{ ref('int_audit_evaluations') }}

),

findings as (

    select *
    from {{ ref('int_findings_enriched') }}

),

actions as (

    select *
    from {{ ref('int_corrective_actions_enriched') }}

),

evaluation_metrics as (

    select

        audit_id,

        count(*) as evaluation_count,

        count(score_maturite)
            as scored_evaluation_count,

        round(
            avg(score_maturite)::numeric,
            2
        ) as avg_maturity_score

    from evaluations

    group by audit_id

),

finding_metrics as (

    select

        audit_id,

        count(*) as all_findings_count,

        count(*) filter (
            where categorie_finding
            not in (
                'Bonne Pratique',
                'NA'
            )
        ) as total_findings_kpi,

        count(*) filter (
            where categorie_finding =
                'NC Mineure'
        ) as nc_mineure_count,

        count(*) filter (
            where categorie_finding =
                'NC Majeure'
        ) as nc_majeure_count,

        count(*) filter (
            where categorie_finding =
                'OFI'
        ) as ofi_count,

        count(*) filter (
            where categorie_finding =
                'Observation'
        ) as observation_count,

        count(*) filter (
            where categorie_finding =
                'Bonne Pratique'
        ) as bonne_pratique_count,

        count(*) filter (
            where categorie_finding =
                'NA'
        ) as na_count

    from findings

    group by audit_id

),

action_metrics as (

    select

        audit_id,

        count(*) as corrective_action_count,

        count(*) filter (
            where lower(
                coalesce(statut, '')
            ) <> 'clôturé'
        ) as open_action_count,

        count(*) filter (
            where indicateur_age =
                'Alerte'
        ) as alert_action_count,

        count(*) filter (
            where indicateur_age =
                'Critique'
        ) as critical_action_count,

        count(*) filter (
            where indicateur_age =
                'Escalade management'
        ) as escalated_action_count

    from actions

    group by audit_id

)

select

    au.audit_id,

    acc.account_id,
    acc.account_name,

    c.campaign_id,
    c.campaign_name,

    au.completion_rate,

    au.current_proposed_status,

    au.current_validated_status
        as official_audit_status,

    case
        when au.current_validated_status
            is null
            then null

        when au.current_validated_status =
            'audite'
            then true

        else false
    end as is_officially_audited,

    coalesce(
        em.evaluation_count,
        0
    ) as evaluation_count,

    coalesce(
        em.scored_evaluation_count,
        0
    ) as scored_evaluation_count,

    em.avg_maturity_score,

    case
        when em.avg_maturity_score is null
            then null

        when em.avg_maturity_score >= 4.5
            then 'Très Performant'

        when em.avg_maturity_score >= 3.5
            then 'Performant'

        when em.avg_maturity_score >= 2.5
            then 'À surveiller'

        when em.avg_maturity_score >= 1.5
            then 'À Risque'

        else 'Critique'
    end as account_badge,

    coalesce(
        fm.all_findings_count,
        0
    ) as all_findings_count,

    coalesce(
        fm.total_findings_kpi,
        0
    ) as total_findings_kpi,

    coalesce(
        fm.nc_mineure_count,
        0
    ) as nc_mineure_count,

    coalesce(
        fm.nc_majeure_count,
        0
    ) as nc_majeure_count,

    coalesce(
        fm.ofi_count,
        0
    ) as ofi_count,

    coalesce(
        fm.observation_count,
        0
    ) as observation_count,

    coalesce(
        fm.bonne_pratique_count,
        0
    ) as bonne_pratique_count,

    coalesce(
        fm.na_count,
        0
    ) as na_count,

    coalesce(
        am.corrective_action_count,
        0
    ) as corrective_action_count,

    coalesce(
        am.open_action_count,
        0
    ) as open_action_count,

    coalesce(
        am.alert_action_count,
        0
    ) as alert_action_count,

    coalesce(
        am.critical_action_count,
        0
    ) as critical_action_count,

    coalesce(
        am.escalated_action_count,
        0
    ) as escalated_action_count

from audits au

join accounts acc
    on au.account_id =
       acc.account_id

join campaigns c
    on au.campaign_id =
       c.campaign_id

left join evaluation_metrics em
    on au.audit_id =
       em.audit_id

left join finding_metrics fm
    on au.audit_id =
       fm.audit_id

left join action_metrics am
    on au.audit_id =
       am.audit_id