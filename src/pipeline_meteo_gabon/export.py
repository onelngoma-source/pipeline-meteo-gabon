"""Exporte les tables analytiques en CSV pour le tableau de bord."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import psycopg

from pipeline_meteo_gabon.load import connexion

logger = logging.getLogger(__name__)

DOSSIER_EXPORT = Path("dashboard/donnees")

REQUETES = {
    "villes": "SELECT * FROM ref.villes ORDER BY nom",
    "meteo_mensuelle": "SELECT * FROM analytique.meteo_mensuelle ORDER BY ville, annee, mois",
    "normales_mensuelles": "SELECT * FROM analytique.normales_mensuelles ORDER BY ville, mois",
    "anomalies_mensuelles": (
        "SELECT * FROM analytique.anomalies_mensuelles ORDER BY ville, annee, mois"
    ),
}


def exporter(conn: psycopg.Connection, dossier: Path) -> dict[str, int]:
    """Écrit un fichier CSV par table et renvoie le nombre de lignes de chacun."""
    dossier.mkdir(parents=True, exist_ok=True)
    resultats = {}
    for nom, requete in REQUETES.items():
        with conn.cursor() as curseur:
            curseur.execute(requete)
            colonnes = [colonne.name for colonne in curseur.description]
            df = pd.DataFrame(curseur.fetchall(), columns=colonnes)
        df.to_csv(dossier / f"{nom}.csv", index=False)
        resultats[nom] = len(df)
    return resultats


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    with connexion() as conn:
        for nom, nombre in exporter(conn, DOSSIER_EXPORT).items():
            logger.info("%s : %d lignes exportées", nom, nombre)


if __name__ == "__main__":
    main()