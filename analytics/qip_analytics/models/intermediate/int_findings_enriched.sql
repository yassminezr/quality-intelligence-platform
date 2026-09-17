with findings as (

    select *
    from {{ ref('stg_findings') }}

),

evaluations as (

    select *
    from {{ ref('int_audit_evaluations') }}

)

select

    f.finding_id,

    e.evaluation_id,

    e.audit_id,

    e.account_id,
    e.account_name,

    e.campaign_id,
    e.campaign_name,

    e.control_id,

    e.clause_id,
    e.clause_iso,
    e.intitule_iso,

    e.libelle_terrain,

    f.categorie_finding,

    e.score_maturite,
    e.niveau_maturite,

    e.constat_auditeur,

    f.created_at

from findings f

join evaluations e
    on f.evaluation_id = e.evaluation_id