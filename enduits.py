"""
enduits.py
==========
Calcul des surfaces d'enduits (verticaux et horizontaux).

A la demande de l'architecte, Sme (surface mur élévation) et Sm (portion
de mur de soubassement hors-sol) sont recalculées ici de façon
indépendante à partir de leurs propres dimensions saisies dans l'onglet
Enduits - plutôt que de systématiquement réutiliser les valeurs déjà
calculées dans l'onglet Maçonnerie (qui restent affichées comme référence,
mais ne servent plus directement au calcul de EnV).

Formules :
    Sme (dans Enduits) = (longueur_mur_elevation x hauteur_mur_elevation) - surface_baies
    Sm  (dans Enduits) = longueur_mur_soubassement_hors_sol x hauteur_mur_soubassement_hors_sol
    EnV = (Sme x 2) + Sm + (Sa x 2)
    EnH = Sp
"""

from .donnees import DonneesEnduits


class CalculEnduits:
    """Calcule les surfaces d'enduits pour un jeu de données donné."""

    def __init__(self, donnees_enduits: DonneesEnduits):
        self.de = donnees_enduits

    def surface_mur_elevation(self) -> float:
        """Sme recalculée indépendamment dans l'onglet Enduits (peut différer
        de la valeur calculée dans l'onglet Maçonnerie)."""
        d = self.de
        return (d.longueur_mur_elevation * d.hauteur_mur_elevation) - d.surface_baies

    def surface_mur_soubassement_hors_sol(self) -> float:
        """Sm recalculée indépendamment dans l'onglet Enduits."""
        d = self.de
        return d.longueur_mur_soubassement_hors_sol * d.hauteur_mur_soubassement_hors_sol

    def surface_enduit_vertical(self) -> float:
        """EnV = enduits verticaux, intérieur + extérieur du mur d'élévation
        (d'où le x2 sur Sme), plus la portion de mur de soubassement hors
        terrain naturel (Sm), plus l'acrotère (Sa), enduit sur ses deux
        faces (d'où le x2 sur Sa)."""
        sme = self.surface_mur_elevation()
        sm = self.surface_mur_soubassement_hors_sol()
        return (sme * 2) + sm + (self.de.surface_acrotere * 2)

    def surface_enduit_horizontal(self) -> float:
        """EnH = enduit horizontal en sous-face du plancher (saisie directe)."""
        return self.de.surface_plancher

    def resume(self) -> dict:
        """Retourne toutes les surfaces d'enduits dans un dict."""
        return {
            "EnV": self.surface_enduit_vertical(),
            "EnH": self.surface_enduit_horizontal(),
        }
