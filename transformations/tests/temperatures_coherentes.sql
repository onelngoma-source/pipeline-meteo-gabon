-- Échoue si la température moyenne n'est pas comprise entre la minimale et la maximale.
select ville, date, temp_min_c, temp_moy_c, temp_max_c
from {{ ref('stg_meteo_quotidienne') }}
where temp_min_c > temp_max_c
    or temp_moy_c < temp_min_c
    or temp_moy_c > temp_max_c