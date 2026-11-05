"""Chargement de l'historique météo dans PostgreSQL, année par année."""

from __future__ import annotations

import argparse
import logging
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from pipeline_meteo_gabon.extract import FUSEAU_HORAIRE, collecter
from pipeline_meteo_gabon.load import charger, connexion

logger = logging.getLogger(__name__)

DELAI_ARCHIVES_JOURS = 7


def periodes_annuelles(debut: date, fin: date) -> list[tuple[date, date]]:
    """Découpe une période en tranches d'une année civile au maximum."""
    if debut > fin:
        raise ValueError("La date de début doit précéder la date de fin")
    periodes = []
    for annee in range(debut.year, fin.year + 1):
        periodes.append((max(debut, date(annee, 1, 1)), min(fin, date(annee, 12, 31))))
    return periodes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("pipeline_meteo_gabon.extract").setLevel(logging.WARNING)

    aujourd_hui = datetime.now(ZoneInfo(FUSEAU_HORAIRE)).date()
    fin_par_defaut = aujourd_hui - timedelta(days=DELAI_ARCHIVES_JOURS)

    parseur = argparse.ArgumentParser(description="Charge l'historique météo année par année.")
    parseur.add_argument("--debut", type=date.fromisoformat, default=date(1990, 1, 1))
    parseur.add_argument("--fin", type=date.fromisoformat, default=fin_par_defaut)
    parseur.add_argument("--pause", type=float, default=2.0, help="Secondes entre deux années")
    arguments = parseur.parse_args()

    dossier = Path("data/raw/historique")
    dossier.mkdir(parents=True, exist_ok=True)

    total = 0
    with connexion() as conn:
        for debut, fin in periodes_annuelles(arguments.debut, arguments.fin):
            df = collecter(debut, fin, archive=True)
            df.to_csv(dossier / f"meteo_{debut.year}.csv", index=False)
            nombre = charger(conn, df)
            total += nombre
            logger.info("Année %d : %d lignes chargées", debut.year, nombre)
            time.sleep(arguments.pause)

    logger.info("Historique terminé : %d lignes chargées au total", total)


if __name__ == "__main__":
    main()