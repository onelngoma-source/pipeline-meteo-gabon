"""Liste des villes suivies par le pipeline : les 9 chefs-lieux de province du Gabon."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Ville:
    nom: str
    province: str
    latitude: float
    longitude: float


VILLES: tuple[Ville, ...] = (
    Ville("Libreville", "Estuaire", 0.3901, 9.4544),
    Ville("Franceville", "Haut-Ogooué", -1.6333, 13.5833),
    Ville("Lambaréné", "Moyen-Ogooué", -0.7001, 10.2406),
    Ville("Mouila", "Ngounié", -1.8685, 11.0559),
    Ville("Tchibanga", "Nyanga", -2.8500, 11.0333),
    Ville("Makokou", "Ogooué-Ivindo", 0.5738, 12.8642),
    Ville("Koulamoutou", "Ogooué-Lolo", -1.1303, 12.4736),
    Ville("Port-Gentil", "Ogooué-Maritime", -0.7193, 8.7815),
    Ville("Oyem", "Woleu-Ntem", 1.5995, 11.5793),
)