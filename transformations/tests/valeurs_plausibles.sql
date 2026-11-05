-- Échoue si une valeur est physiquement impossible pour le climat du Gabon.
select ville, date, temp_min_c, temp_max_c, pluie_mm, vent_max_kmh
from {{ ref('stg_meteo_quotidienne') }}
where pluie_mm < 0
    or pluie_mm > 500
    or temp_max_c > 45
    or temp_min_c < 5
    or vent_max_kmh < 0