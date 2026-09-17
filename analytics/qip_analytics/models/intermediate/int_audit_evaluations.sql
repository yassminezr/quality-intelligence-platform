with evaluations as (

    select *
    from {{ ref('stg_evaluations') }}

),

audits as (

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

controls as (

    select *
    from {{ ref('stg_iso_controls') }}

),

clauses as (

    select *
    from {{ ref('stg_iso_clauses') }}

)

select

    e.evaluation_id,

    a.audit_id,

    acc.account_id,
    acc.account_name,

    c.campaign_id,
    c.campaign_name,

    ctrl.control_id,

    cl.clause_id,
    cl.clause_iso,
    cl.intitule_iso,

    ctrl.libelle_terrain,
    ctrl.controle_attendu,
    ctrl.categorie_scope,

    e.score_maturite,
    e.niveau_maturite,
    e.constat_auditeur,
    e.evidence,
    e.commentaires,

    a.completion_rate,
    a.current_proposed_status,
    a.current_validated_status,

    e.created_at,
    e.updated_at

from evaluations e

join audits a
    on e.audit_id = a.audit_id

join accounts acc
    on a.account_id = acc.account_id

join campaigns c
    on a.campaign_id = c.campaign_id

join controls ctrl
    on e.control_id = ctrl.control_id

join clauses cl
    on ctrl.clause_id = cl.clause_id