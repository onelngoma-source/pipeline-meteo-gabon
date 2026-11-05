-- Données quotidiennes nettoyées : noms de colonnes en français, unités explicites, province ajoutée.

with meteo as (
    select * from {{ source('brut', 'meteo_quotidienne') }}
),

villes as (
    select * from {{ source('ref', 'villes') }}
)

select
    meteo.ville,
    villes.province,
    meteo.date,
    extract(year from meteo.date)::int as annee,
    extract(month from meteo.date)::int as mois,
    meteo.temperature_2m_max as temp_max_c,
    meteo.temperature_2m_min as temp_min_c,
    meteo.temperature_2m_mean as temp_moy_c,
    meteo.precipitation_sum as pluie_mm,
    meteo.wind_speed_10m_max as vent_max_kmh,
    meteo.source,
    meteo.collecte_le
from meteo
inner join villes on villes.nom = meteo.ville