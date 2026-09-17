select
    *
from {{ ref('mart_corrective_actions') }}
where categorie_finding = 'NA'