import pytest

from pipeline_meteo_gabon.config import VILLES
from pipeline_meteo_gabon.extract import json_vers_dataframe


def test_les_neuf_chefs_lieux_sont_presents():
    assert len(VILLES) == 9
    assert len({ville.nom for ville in VILLES}) == 9


def test_coordonnees_dans_le_gabon():
    for ville in VILLES:
        assert -4.0 < ville.latitude < 2.5
        assert 8.5 < ville.longitude < 14.6


def test_json_vers_dataframe():
    exemple = {
        "daily": {
            "time": ["2026-11-01", "2026-11-02"],
            "temperature_2m_max": [30.1, 29.5],
            "precipitation_sum": [12.0, 0.0],
        }
    }
    df = json_vers_dataframe(exemple, VILLES[0])
    assert len(df) == 2
    assert list(df.columns[:3]) == ["ville", "province", "date"]
    assert (df["ville"] == "Libreville").all()


def test_reponse_invalide():
    with pytest.raises(ValueError):
        json_vers_dataframe({}, VILLES[0])