"""
terrassement.py
================
Calcul des quantités de terrassement à partir des données saisies
(DonneesTerrassement).

Formules (voir avant-métré de référence) :
    Vf   = (Ldfr x Ht x l) + Sum(Si x Htt x ni)
    Vrtal = Sl x eprl
    Vrtac = Sc x eprc
    Vmse  = ldms x Htmse x Epm   (utile pour calculer Vrpf ailleurs)
"""

from .donnees import DonneesTerrassement


class CalculTerrassement:
    """Calcule les quantités de terrassement pour un jeu de données donné."""

    def __init__(self, donnees: DonneesTerrassement):
        self.donnees = donnees

    def volume_fouille_rigole(self) -> float:
        """Volume de la fouille en rigole (tranchée continue)."""
        d = self.donnees
        return d.longueur_developpee_rigole * d.profondeur_rigole * d.largeur_rigole

    def volume_fouilles_en_trous(self) -> float:
        """Volume cumulé de toutes les fouilles en trous (semelles isolées)."""
        d = self.donnees
        return sum(f.surface * d.profondeur_fouille_trou * f.nombre
                   for f in d.fouilles_en_trous)

    def volume_fouilles(self) -> float:
        """Vf = volume total des fouilles (rigole + trous)."""
        return self.volume_fouille_rigole() + self.volume_fouilles_en_trous()

    def volume_remblai_apport_locaux(self) -> float:
        """Vrtal = volume de terre d'apport pour les locaux."""
        d = self.donnees
        return d.surface_locaux * d.epaisseur_remblai_locaux

    def volume_remblai_apport_cour(self) -> float:
        """Vrtac = volume de terre d'apport pour la cour."""
        d = self.donnees
        return d.surface_cour * d.epaisseur_remblai_cour

    def volume_mur_sous_bassement_enterre(self) -> float:
        """Vmse = volume du mur de soubassement enterré.
        Utilisé (hors de ce module) pour calculer le remblai provenant
        des fouilles (Vrpf), avec les volumes de béton."""
        d = self.donnees
        return (d.longueur_developpee_mur_sous_bassement
                * d.hauteur_mur_sous_bassement_enterre
                * d.epaisseur_mur_sous_bassement)

    def resume(self) -> dict:
        """Retourne toutes les quantités de terrassement dans un dict,
        pratique pour l'affichage et pour les transmettre à projet.py."""
        return {
            "Vf": self.volume_fouilles(),
            "Vrtal": self.volume_remblai_apport_locaux(),
            "Vrtac": self.volume_remblai_apport_cour(),
            "Vmse": self.volume_mur_sous_bassement_enterre(),
        }
