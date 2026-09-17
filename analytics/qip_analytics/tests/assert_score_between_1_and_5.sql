select
    *
from {{ ref('stg_evaluations') }}
where score_maturite is not null
  and (
      score_maturite < 1
      or score_maturite > 5
  )