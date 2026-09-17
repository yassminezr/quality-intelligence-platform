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

controls as (

    select *
    from {{ ref('stg_iso_controls') }}

),

clauses as (

    select *
    from {{ ref('stg_iso_clauses') }}

),

evaluations as (

    select *
    from {{ ref('stg_evaluations') }}

),

findings as (

    select *
    from {{ ref('stg_findings') }}

),

actions as (

    select *
    from {{ ref('stg_corrective_actions') }}

)

select

    -- =========================
    -- Audit / Account
    -- =========================

    au.audit_id,

    acc.account_id,
    acc.account_name,

    c.campaign_id,
    c.campaign_name,

    au.completion_rate,

    au.current_proposed_status,
    au.current_validated_status
        as official_audit_status,

    -- =========================
    -- ISO Reference
    -- =========================

    ctrl.control_id,

    cl.clause_id,
    cl.clause_iso,
    cl.intitule_iso,

    ctrl.libelle_terrain,
    ctrl.controle_attendu,
    ctrl.categorie_scope,
    ctrl.reference_edge,
    ctrl.preuves_attendues,

    -- =========================
    -- Evaluation
    -- =========================

    e.evaluation_id,

    e.score_maturite,
    e.niveau_maturite,
    e.constat_auditeur,
    e.evidence,
    e.commentaires,

    case
        when e.evaluation_id is not null
            then true
        else false
    end as evaluation_started,

    case
        when e.score_maturite is not null
            then true
        else false
    end as clause_scored,

    -- =========================
    -- Finding
    -- =========================

    f.finding_id,
    f.categorie_finding,

    case
        when f.categorie_finding
             not in (
                 'Bonne Pratique',
                 'NA'
             )
            then true
        else false
    end as is_counted_in_total_findings,

    -- =========================
    -- Corrective Action
    -- =========================

    ca.action_id,

    ca.action_text,
    ca.responsable,

    ca.date_debut,
    ca.date_cloture,

    ca.statut as action_status,

    -- =========================
    -- Age Action
    -- =========================

    case

        when ca.date_debut is null
            then null

        when lower(
            coalesce(
                ca.statut,
                ''
            )
        ) = 'clôturé'
        and ca.date_cloture is not null

            then
                ca.date_cloture
                - ca.date_debut

        else
            current_date
            - ca.date_debut

    end as age_jours,

    -- =========================
    -- Age Indicator
    -- =========================

    case

        when ca.date_debut is null
            then null

        when (
            case
                when lower(
                    coalesce(
                        ca.statut,
                        ''
                    )
                ) = 'clôturé'
                and ca.date_cloture
                    is not null

                then
                    ca.date_cloture
                    - ca.date_debut

                else
                    current_date
                    - ca.date_debut
            end
        ) <= 30
            then 'Normal'

        when (
            case
                when lower(
                    coalesce(
                        ca.statut,
                        ''
                    )
                ) = 'clôturé'
                and ca.date_cloture
                    is not null

                then
                    ca.date_cloture
                    - ca.date_debut

                else
                    current_date
                    - ca.date_debut
            end
        ) <= 60
            then 'Alerte'

        when (
            case
                when lower(
                    coalesce(
                        ca.statut,
                        ''
                    )
                ) = 'clôturé'
                and ca.date_cloture
                    is not null

                then
                    ca.date_cloture
                    - ca.date_debut

                else
                    current_date
                    - ca.date_debut
            end
        ) <= 90
            then 'Critique'

        else
            'Escalade management'

    end as indicateur_age

from audits au

join accounts acc
    on au.account_id =
       acc.account_id

join campaigns c
    on au.campaign_id =
       c.campaign_id

-- Une grille complète :
-- chaque audit × chaque contrôle ISO
cross join controls ctrl

join clauses cl
    on ctrl.clause_id =
       cl.clause_id

left join evaluations e
    on e.audit_id =
       au.audit_id
    and e.control_id =
       ctrl.control_id

left join findings f
    on f.evaluation_id =
       e.evaluation_id

left join actions ca
    on ca.finding_id =
       f.finding_id