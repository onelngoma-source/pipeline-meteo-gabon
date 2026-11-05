-- Échoue si une ville a plusieurs lignes pour le même mois.
select ville, annee, mois, count(*) as nb
from {{ ref('meteo_mensuelle') }}
group by ville, annee, mois
having count(*) > 1