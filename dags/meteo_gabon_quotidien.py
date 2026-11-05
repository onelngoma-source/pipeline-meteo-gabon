"""Collecte quotidienne de la météo des 9 chefs-lieux de province du Gabon."""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag, get_current_context, task

FUSEAU = pendulum.timezone("Africa/Libreville")
DBT = os.environ.get("DBT_EXECUTABLE", "/opt/dbt-venv/bin/dbt")
PROJET_DBT = os.environ.get("DBT_PROJET", "/opt/airflow/transformations")


@dag(
    dag_id="meteo_gabon_quotidien",
    description="Collecte, chargement et contrôle de la météo de la veille pour les 9 provinces",
    schedule="30 7 * * *",
    start_date=pendulum.datetime(2026, 11, 1, tz=FUSEAU),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=10)},
    tags=["meteo", "gabon"],
)
def meteo_gabon_quotidien():
    @task
    def determiner_jour() -> str:
        """Renvoie la date de la veille (heure de Libreville) au format AAAA-MM-JJ."""
        contexte = get_current_context()
        reference = contexte.get("logical_date") or pendulum.now(FUSEAU)
        veille = pendulum.instance(reference).in_timezone(FUSEAU).date() - timedelta(days=1)
        return veille.isoformat()

    @task
    def extraire(jour: str) -> str:
        """Collecte la météo du jour demandé et l'enregistre en CSV."""
        from datetime import date

        from pipeline_meteo_gabon.extract import collecter

        journee = date.fromisoformat(jour)
        df = collecter(journee, journee)
        dossier = Path(os.environ.get("DOSSIER_DONNEES", "data")) / "raw" / "quotidien"
        dossier.mkdir(parents=True, exist_ok=True)
        chemin = dossier / f"meteo_{jour}.csv"
        df.to_csv(chemin, index=False)
        return str(chemin)

    @task
    def charger_fichier(chemin: str) -> int:
        """Charge le fichier CSV dans PostgreSQL (sans doublons)."""
        import pandas as pd

        from pipeline_meteo_gabon.load import charger, connexion

        with connexion() as conn:
            return charger(conn, pd.read_csv(chemin))

    @task
    def verifier(jour: str) -> None:
        """Vérifie que les 9 villes sont bien présentes dans la base pour ce jour."""
        from pipeline_meteo_gabon.config import VILLES
        from pipeline_meteo_gabon.load import connexion

        with connexion() as conn:
            (lignes,) = conn.execute(
                "SELECT COUNT(*) FROM brut.meteo_quotidienne WHERE date = %s", (jour,)
            ).fetchone()
        if lignes != len(VILLES):
            raise ValueError(f"{lignes} lignes trouvées pour le {jour}, {len(VILLES)} attendues")

    transformer = BashOperator(
        task_id="transformer_dbt",
        bash_command=(
            f"{DBT} build --project-dir {PROJET_DBT} --profiles-dir {PROJET_DBT} "
            "--target-path /tmp/dbt/target --log-path /tmp/dbt/logs"
        ),
    )

    jour = determiner_jour()
    chemin = extraire(jour)
    chargement = charger_fichier(chemin)
    chargement >> verifier(jour) >> transformer


meteo_gabon_quotidien()