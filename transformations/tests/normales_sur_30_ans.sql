-- Échoue si une normale n'est pas calculée sur exactement 30 années complètes.
select ville, mois, nb_annees
from {{ ref('normales_mensuelles') }}
where nb_annees <> {{ var('normale_fin') }} - {{ var('normale_debut') }} + 1