import math

import pandas as pd
import pytest

from pipeline_meteo_gabon.load import COLONNES, preparer_lignes


def exemple() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ville": ["Libreville", "Oyem"],
            "province": ["Estuaire", "Woleu-Ntem"],
            "date": ["2026-10-01", "2026-10-01"],
            "temperature_2m_max": [28.4, 27.9],
            "temperature_2m_min": [24.9, 20.1],
            "temperature_2m_mean": [26.6, 23.4],
            "precipitation_sum": [5.2, math.nan],
            "wind_speed_10m_max": [18.9, 9.4],
            "source": ["archive", "archive"],
        }
    )


def test_preparer_lignes_garde_les_bonnes_colonnes():
    lignes = preparer_lignes(exemple())
    assert len(lignes) == 2
    assert len(lignes[0]) == len(COLONNES)
    assert lignes[0][0] == "Libreville"


def test_valeur_manquante_devient_none():
    lignes = preparer_lignes(exemple())
    assert lignes[1][COLONNES.index("precipitation_sum")] is None


def test_colonne_manquante():
    with pytest.raises(ValueError, match="source"):
        preparer_lignes(exemple().drop(columns="source"))