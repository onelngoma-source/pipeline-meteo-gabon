# Pipeline météo du Gabon

Pipeline de données qui collecte chaque jour la météo des 9 chefs-lieux de province du Gabon, la stocke, la transforme et l'affiche dans un tableau de bord.

## Statut

Projet en cours de construction.

- [x] Collecte depuis l'API Open-Meteo (prévisions et archives)
- [ ] Stockage dans PostgreSQL
- [ ] Chargement de l'historique
- [ ] Orchestration quotidienne avec Airflow
- [ ] Transformations et contrôles qualité
- [ ] Tableau de bord

## Lancer la collecte

```bash
uv sync
uv run python -m pipeline_meteo_gabon.extract
uv run python -m pipeline_meteo_gabon.extract --debut 2026-10-01 --fin 2026-10-31 --archive
```

## Tests

```bash
uv run pytest
```

Données météo : [Open-Meteo](https://open-meteo.com/).