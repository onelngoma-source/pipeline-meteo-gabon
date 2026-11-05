-- Normales climatiques par ville et par mois, calculées sur 30 ans (période de référence 1991-2020).

with mensuel as (
    select * from {{ ref('meteo_mensuelle') }}
)

select
    ville,
    province,
    mois,
    round(avg(temp_moy_c), 2) as temp_moy_normale_c,
    round(avg(pluie_mm), 1) as pluie_normale_mm,
    round(avg(jours_de_pluie), 1) as jours_de_pluie_normaux,
    count(*) as nb_annees
from mensuel
where annee between {{ var('normale_debut') }} and {{ var('normale_fin') }}
    and mois_complet
group by ville, province, mois