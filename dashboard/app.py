"""Tableau de bord du climat des 9 chefs-lieux de province du Gabon (1990 à aujourd'hui)."""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

DOSSIER_DONNEES = Path(__file__).parent / "donnees"
NOMS_MOIS = [
    "Jan",
    "Fév",
    "Mar",
    "Avr",
    "Mai",
    "Juin",
    "Juil",
    "Août",
    "Sep",
    "Oct",
    "Nov",
    "Déc",
]
COULEUR_PLUIE = "#2E86C1"
COULEUR_TEMP = "#E67E22"

st.set_page_config(page_title="Climat du Gabon", page_icon="🌦️", layout="wide")


@st.cache_data
def charger(nom: str) -> pd.DataFrame:
    return pd.read_csv(DOSSIER_DONNEES / f"{nom}.csv")


@st.cache_data
def calculer_annuel(mensuel: pd.DataFrame) -> pd.DataFrame:
    """Moyennes et cumuls annuels, uniquement pour les années dont les 12 mois sont complets."""
    complet = mensuel[mensuel["mois_complet"]]
    annuel = (
        complet.groupby(["ville", "annee"])
        .agg(
            temp_moy_c=("temp_moy_c", "mean"),
            pluie_mm=("pluie_mm", "sum"),
            nb_mois=("mois", "count"),
        )
        .reset_index()
    )
    return annuel[annuel["nb_mois"] == 12]


def tendance_par_decennie(annuel_ville: pd.DataFrame) -> tuple[float, np.ndarray]:
    """Pente de la droite de régression des températures annuelles, en °C par décennie."""
    pente, origine = np.polyfit(annuel_ville["annee"], annuel_ville["temp_moy_c"], 1)
    return pente * 10, pente * annuel_ville["annee"].to_numpy() + origine


villes = charger("villes")
mensuel = charger("meteo_mensuelle")
normales = charger("normales_mensuelles")
anomalies = charger("anomalies_mensuelles")
annuel = calculer_annuel(mensuel)

noms_villes = sorted(villes["nom"])
ville = st.sidebar.selectbox(
    "Ville", noms_villes, index=noms_villes.index("Libreville")
)
st.sidebar.caption(
    "Données : Open-Meteo (réanalyses météorologiques). "
    "Normales calculées sur la période de référence 1991-2020."
)

normales_ville = normales[normales["ville"] == ville].sort_values("mois")
annuel_ville = annuel[annuel["ville"] == ville].sort_values("annee")
anomalies_ville = anomalies[anomalies["ville"] == ville]
dernier_mois = anomalies_ville.sort_values(["annee", "mois"]).iloc[-1]
tendance, droite = tendance_par_decennie(annuel_ville)

st.title("🌦️ Le climat des 9 provinces du Gabon")
st.markdown(
    f"Données quotidiennes de **{annuel['annee'].min()} à aujourd'hui**, collectées chaque matin "
    "par un pipeline automatisé (Airflow, PostgreSQL, dbt)."
)

st.header(f"{ville}")
colonne1, colonne2, colonne3, colonne4 = st.columns(4)
colonne1.metric(
    "Température moyenne normale",
    f"{normales_ville['temp_moy_normale_c'].mean():.1f} °C",
)
colonne2.metric(
    "Pluie annuelle normale",
    f"{normales_ville['pluie_normale_mm'].sum():,.0f} mm".replace(",", " "),
)
colonne3.metric(
    f"{NOMS_MOIS[int(dernier_mois['mois']) - 1]} {int(dernier_mois['annee'])} vs normale",
    f"{dernier_mois['temp_moy_c']:.1f} °C",
    f"{dernier_mois['ecart_temp_c']:+.2f} °C",
    delta_color="inverse",
)
colonne4.metric(
    f"Tendance par décennie ({int(annuel_ville['annee'].min())}-{int(annuel_ville['annee'].max())})",
    f"{tendance:+.2f} °C",
)

gauche, droite_colonne = st.columns(2)

with gauche:
    st.subheader("Climatogramme (normales 1991-2020)")
    climatogramme = make_subplots(specs=[[{"secondary_y": True}]])
    climatogramme.add_trace(
        go.Bar(
            x=NOMS_MOIS,
            y=normales_ville["pluie_normale_mm"],
            name="Pluie (mm)",
            marker_color=COULEUR_PLUIE,
        ),
        secondary_y=False,
    )
    climatogramme.add_trace(
        go.Scatter(
            x=NOMS_MOIS,
            y=normales_ville["temp_moy_normale_c"],
            name="Température (°C)",
            mode="lines+markers",
            line={"color": COULEUR_TEMP, "width": 3},
        ),
        secondary_y=True,
    )
    climatogramme.update_yaxes(title_text="Pluie (mm)", secondary_y=False)
    climatogramme.update_yaxes(
        title_text="Température (°C)", tickformat=".1f", secondary_y=True
    )
    climatogramme.update_layout(
        legend={"orientation": "h", "y": -0.15}, margin={"t": 10}
    )
    st.plotly_chart(climatogramme, width="stretch")

with droite_colonne:
    st.subheader("Évolution de la température annuelle")
    evolution = go.Figure()
    evolution.add_trace(
        go.Scatter(
            x=annuel_ville["annee"],
            y=annuel_ville["temp_moy_c"],
            name="Moyenne annuelle",
            mode="lines+markers",
            line={"color": COULEUR_TEMP},
        )
    )
    evolution.add_trace(
        go.Scatter(
            x=annuel_ville["annee"],
            y=droite,
            name=f"Tendance ({tendance:+.2f} °C / décennie)",
            mode="lines",
            line={"color": "grey", "dash": "dash"},
        )
    )
    evolution.update_layout(
        yaxis_title="Température (°C)",
        legend={"orientation": "h", "y": -0.15},
        margin={"t": 10},
    )
    st.plotly_chart(evolution, width="stretch")

st.subheader("Écart de température à la normale, mois par mois")
st.caption("Rouge : mois plus chaud que la normale 1991-2020. Bleu : mois plus frais.")
grille = anomalies_ville.pivot_table(
    index="annee", columns="mois", values="ecart_temp_c"
)
grille.columns = [NOMS_MOIS[m - 1] for m in grille.columns]
limite = float(np.nanmax(np.abs(grille.to_numpy())))
carte_chaleur = px.imshow(
    grille.T,
    color_continuous_scale="RdBu_r",
    zmin=-limite,
    zmax=limite,
    aspect="auto",
    labels={"x": "Année", "y": "Mois", "color": "Écart (°C)"},
)
carte_chaleur.update_layout(margin={"t": 10})
st.plotly_chart(carte_chaleur, width="stretch")

st.header("Comparaison des 9 provinces")
carte, pluie = st.columns(2)

with carte:
    st.subheader("Localisation")
    st.map(villes, latitude="latitude", longitude="longitude", size=12000, zoom=5)

with pluie:
    st.subheader("Pluie annuelle normale par ville")
    pluie_villes = (
        normales.groupby(["ville", "province"])["pluie_normale_mm"]
        .sum()
        .reset_index()
        .sort_values("pluie_normale_mm")
    )
    pluie_villes["selection"] = np.where(
        pluie_villes["ville"] == ville, "Ville choisie", "Autres villes"
    )
    barres = px.bar(
        pluie_villes,
        x="pluie_normale_mm",
        y="ville",
        orientation="h",
        color="selection",
        color_discrete_map={"Ville choisie": COULEUR_PLUIE, "Autres villes": "#AEB6BF"},
        hover_data=["province"],
        labels={"pluie_normale_mm": "Pluie (mm / an)", "ville": ""},
    )
    barres.update_layout(showlegend=False, margin={"t": 10})
    st.plotly_chart(barres, width="stretch")

st.subheader("Les 10 mois les plus chauds par rapport à la normale")
top = anomalies.sort_values("ecart_temp_c", ascending=False).head(10).copy()
top["mois"] = top["mois"].map(lambda m: NOMS_MOIS[m - 1])
st.dataframe(
    top[
        [
            "ville",
            "province",
            "annee",
            "mois",
            "temp_moy_c",
            "temp_moy_normale_c",
            "ecart_temp_c",
        ]
    ].rename(
        columns={
            "ville": "Ville",
            "province": "Province",
            "annee": "Année",
            "mois": "Mois",
            "temp_moy_c": "Température (°C)",
            "temp_moy_normale_c": "Normale (°C)",
            "ecart_temp_c": "Écart (°C)",
        }
    ),
    hide_index=True,
    width="stretch",
)

st.caption(
    "Ces données proviennent de modèles de réanalyse météorologique et non de stations au sol : "
    "elles sont adaptées aux comparaisons et aux tendances, mais peuvent différer des relevés locaux."
)