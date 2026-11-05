CREATE SCHEMA IF NOT EXISTS ref;
CREATE SCHEMA IF NOT EXISTS brut;

CREATE TABLE IF NOT EXISTS ref.villes (
    nom        TEXT PRIMARY KEY,
    province   TEXT NOT NULL,
    latitude   NUMERIC(7, 4) NOT NULL,
    longitude  NUMERIC(7, 4) NOT NULL
);

CREATE TABLE IF NOT EXISTS brut.meteo_quotidienne (
    ville               TEXT NOT NULL REFERENCES ref.villes (nom),
    date                DATE NOT NULL,
    temperature_2m_max  NUMERIC(5, 1),
    temperature_2m_min  NUMERIC(5, 1),
    temperature_2m_mean NUMERIC(5, 1),
    precipitation_sum   NUMERIC(6, 1),
    wind_speed_10m_max  NUMERIC(5, 1),
    source              TEXT NOT NULL CHECK (source IN ('previsions', 'archive')),
    collecte_le         TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (ville, date)
);