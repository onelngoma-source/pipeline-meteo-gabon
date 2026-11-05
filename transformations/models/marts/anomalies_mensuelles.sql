-- Écart de chaque mois à sa normale : un mois plus chaud ou plus pluvieux que d'habitude ressort ici.

with mensuel as (
    select * from {{ ref('meteo_mensuelle') }}
    where mois_complet
),

normales as (
    select * from {{ ref('normales_mensuelles') }}
)

select
    mensuel.ville,
    mensuel.province,
    mensuel.annee,
    mensuel.mois,
    mensuel.debut_mois,
    mensuel.temp_moy_c,
    normales.temp_moy_normale_c,
    round(mensuel.temp_moy_c - normales.temp_moy_normale_c, 2) as ecart_temp_c,
    mensuel.pluie_mm,
    normales.pluie_normale_mm,
    round(
        100 * (mensuel.pluie_mm - normales.pluie_normale_mm) / nullif(normales.pluie_normale_mm, 0),
        1
    ) as ecart_pluie_pct
from mensuel
inner join normales
    on normales.ville = mensuel.ville
    and normales.mois = mensuel.mois