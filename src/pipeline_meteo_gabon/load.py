"""Chargement des données météo dans PostgreSQL, sans doublons."""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv

from pipeline_meteo_gabon.config import VILLES

logger = logging.getLogger(__name__)

COLONNES = [
    "ville",
    "date",
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_max",
    "source",
]

REQUETE_VILLES = """
    INSERT INTO ref.villes (nom, province, latitude, longitude)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (nom) DO UPDATE SET
        province = EXCLUDED.province,
        latitude = EXCLUDED.latitude,
        longitude = EXCLUDED.longitude
"""

REQUETE_METEO = """
    INSERT INTO brut.meteo_quotidienne (
        ville, date, temperature_2m_max, temperature_2m_min, temperature_2m_mean,
        precipitation_sum, wind_speed_10m_max, source
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (ville, date) DO UPDATE SET
        temperature_2m_max = EXCLUDED.temperature_2m_max,
        temperature_2m_min = EXCLUDED.temperature_2m_min,
        temperature_2m_mean = EXCLUDED.temperature_2m_mean,
        precipitation_sum = EXCLUDED.precipitation_sum,
        wind_speed_10m_max = EXCLUDED.wind_speed_10m_max,
        source = EXCLUDED.source,
        collecte_le = now()
"""


def connexion() -> psycopg.Connection:
    """Ouvre une connexion à PostgreSQL avec les paramètres du fichier .env."""
    load_dotenv()
    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
    )


def preparer_lignes(df: pd.DataFrame) -> list[tuple]:
    """Vérifie les colonnes et convertit le tableau en lignes prêtes à insérer."""
    manquantes = set(COLONNES) - set(df.columns)
    if manquantes:
        raise ValueError(f"Colonnes manquantes : {sorted(manquantes)}")
    donnees = df[COLONNES].astype(object)
    donnees = donnees.where(donnees.notna(), None)
    return list(donnees.itertuples(index=False, name=None))


def charger(conn: psycopg.Connection, df: pd.DataFrame) -> int:
    """Insère ou met à jour les villes et les mesures météo dans la base."""
    lignes = preparer_lignes(df)
    with conn.cursor() as curseur:
        curseur.executemany(
            REQUETE_VILLES,
            [(v.nom, v.province, v.latitude, v.longitude) for v in VILLES],
        )
        curseur.executemany(REQUETE_METEO, lignes)
    conn.commit()
    return len(lignes)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parseur = argparse.ArgumentParser(description="Charge des fichiers CSV météo dans PostgreSQL.")
    parseur.add_argument("fichiers", nargs="+", type=Path, help="Fichiers CSV à charger")
    arguments = parseur.parse_args()

    with connexion() as conn:
        for fichier in arguments.fichiers:
            df = pd.read_csv(fichier)
            nombre = charger(conn, df)
            logger.info("%d lignes chargées depuis %s", nombre, fichier)


if __name__ == "__main__":
    main()