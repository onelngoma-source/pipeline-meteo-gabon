"""Collecte des données météo quotidiennes depuis l'API Open-Meteo."""

from __future__ import annotations

import argparse
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pipeline_meteo_gabon.config import VILLES, Ville

logger = logging.getLogger(__name__)

URL_PREVISIONS = "https://api.open-meteo.com/v1/forecast"
URL_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
FUSEAU_HORAIRE = "Africa/Libreville"
VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_max",
]


def creer_session() -> requests.Session:
    """Crée une session HTTP qui réessaie automatiquement en cas d'erreur temporaire."""
    session = requests.Session()
    reessais = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    session.mount("https://", HTTPAdapter(max_retries=reessais))
    return session


def recuperer_meteo(
    session: requests.Session, ville: Ville, debut: date, fin: date, archive: bool = False
) -> dict:
    """Interroge l'API pour une ville et une période, et renvoie la réponse JSON."""
    url = URL_ARCHIVE if archive else URL_PREVISIONS
    parametres = {
        "latitude": ville.latitude,
        "longitude": ville.longitude,
        "start_date": debut.isoformat(),
        "end_date": fin.isoformat(),
        "daily": ",".join(VARIABLES),
        "timezone": FUSEAU_HORAIRE,
    }
    reponse = session.get(url, params=parametres, timeout=30)
    reponse.raise_for_status()
    return reponse.json()


def json_vers_dataframe(donnees: dict, ville: Ville) -> pd.DataFrame:
    """Transforme la réponse de l'API en tableau : une ligne par ville et par jour."""
    quotidien = donnees.get("daily")
    if not quotidien or "time" not in quotidien:
        raise ValueError(f"Réponse inattendue de l'API pour {ville.nom}")
    df = pd.DataFrame(quotidien).rename(columns={"time": "date"})
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df.insert(0, "ville", ville.nom)
    df.insert(1, "province", ville.province)
    return df


def collecter(debut: date, fin: date, archive: bool = False) -> pd.DataFrame:
    """Collecte la météo de toutes les villes sur la période demandée."""
    session = creer_session()
    tableaux = []
    for ville in VILLES:
        logger.info("Collecte de %s du %s au %s", ville.nom, debut, fin)
        donnees = recuperer_meteo(session, ville, debut, fin, archive)
        tableaux.append(json_vers_dataframe(donnees, ville))
    df = pd.concat(tableaux, ignore_index=True)
    df["source"] = "archive" if archive else "previsions"
    return df


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parseur = argparse.ArgumentParser(description="Collecte la météo des villes du Gabon.")
    parseur.add_argument("--debut", type=date.fromisoformat, help="Date de début (AAAA-MM-JJ)")
    parseur.add_argument("--fin", type=date.fromisoformat, help="Date de fin (AAAA-MM-JJ)")
    parseur.add_argument("--archive", action="store_true", help="Utiliser l'API d'archives")
    arguments = parseur.parse_args()

    aujourd_hui = datetime.now(ZoneInfo(FUSEAU_HORAIRE)).date()
    hier = aujourd_hui - timedelta(days=1)
    debut = arguments.debut or hier
    fin = arguments.fin or hier

    df = collecter(debut, fin, arguments.archive)

    dossier = Path("data/raw")
    dossier.mkdir(parents=True, exist_ok=True)
    chemin = dossier / f"meteo_{debut}_{fin}.csv"
    df.to_csv(chemin, index=False)
    logger.info("%d lignes enregistrées dans %s", len(df), chemin)


if __name__ == "__main__":
    main()