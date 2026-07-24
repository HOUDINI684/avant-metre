"""
maconnerie.py
=============
Calcul des surfaces de murs en agglos (parpaings) à partir des données
saisies (DonneesAgglos), en réutilisant ldms depuis DonneesTerrassement
(le mur de soubassement suit la même longueur développée que les fouilles).

Formules :
    Smsb = ldms x Htms
    Sme  = (ldme x Htme) - Sb
"""

from .donnees import DonneesAgglos, DonneesTerrassement


class CalculMaconnerie:
    """Calcule les surfaces de murs en agglos pour un jeu de données donné."""

    def __init__(self, donnees_terrassement: DonneesTerrassement, donnees_agglos: DonneesAgglos):
        self.dt = donnees_terrassement
        self.da = donnees_agglos

    def surface_mur_soubassement(self) -> float:
        """Smsb = surface du mur de soubassement (enterré)."""
        return self.dt.longueur_developpee_mur_sous_bassement * self.da.hauteur_mur_soubassement

    def surface_mur_elevation(self) -> float:
        """Sme = surface du mur en élévation, moins les baies (portes/fenêtres)."""
        da = self.da
        return (da.longueur_developpee_mur_elevation * da.hauteur_mur_elevation) - da.surface_baies

    def resume(self) -> dict:
        """Retourne toutes les surfaces de maçonnerie dans un dict."""
        return {
            "Smsb": self.surface_mur_soubassement(),
            "Sme": self.surface_mur_elevation(),
        }
