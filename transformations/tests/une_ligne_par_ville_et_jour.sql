-- Échoue si une ville a plusieurs lignes pour le même jour.
select ville, date, count(*) as nb
from {{ ref('stg_meteo_quotidienne') }}
group by ville, date
having count(*) > 1