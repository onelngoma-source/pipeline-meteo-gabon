from datetime import date

import pytest

from pipeline_meteo_gabon.backfill import periodes_annuelles


def test_decoupage_sur_plusieurs_annees():
    periodes = periodes_annuelles(date(2024, 6, 15), date(2026, 3, 10))
    assert periodes == [
        (date(2024, 6, 15), date(2024, 12, 31)),
        (date(2025, 1, 1), date(2025, 12, 31)),
        (date(2026, 1, 1), date(2026, 3, 10)),
    ]


def test_periode_dans_une_seule_annee():
    assert periodes_annuelles(date(2026, 2, 1), date(2026, 2, 28)) == [
        (date(2026, 2, 1), date(2026, 2, 28))
    ]


def test_dates_inversees():
    with pytest.raises(ValueError):
        periodes_annuelles(date(2026, 1, 2), date(2026, 1, 1))