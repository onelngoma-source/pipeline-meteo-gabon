-- Agrégats mensuels par ville : températures moyennes, cumul de pluie et jours de pluie.

with quotidien as (
    select * from {{ ref('stg_meteo_quotidienne') }}
)

select
    ville,
    province,
    annee,
    mois,
    make_date(annee, mois, 1) as debut_mois,
    count(*) as nb_jours,
    count(*) = extract(day from make_date(annee, mois, 1) + interval '1 month - 1 day')::int
        as mois_complet,
    round(avg(temp_moy_c), 2) as temp_moy_c,
    round(avg(temp_max_c), 2) as temp_max_moy_c,
    round(avg(temp_min_c), 2) as temp_min_moy_c,
    max(temp_max_c) as temp_max_record_c,
    round(sum(pluie_mm), 1) as pluie_mm,
    count(*) filter (where pluie_mm >= 1) as jours_de_pluie
from quotidien
group by ville, province, annee, mois