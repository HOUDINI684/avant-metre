"""
projet.py
=========
Classe orchestratrice de l'avant-métré : assemble les 4 modules de calcul
(terrassement, béton, maçonnerie, enduits), calcule les quantités qui
dépendent de plusieurs modules à la fois (comme Vrpf), et génère le
tableau récapitulatif final.
"""

from .donnees import DonneesTerrassement, DonneesBeton, DonneesAgglos, DonneesEnduits
from .terrassement import CalculTerrassement
from .beton import CalculBeton
from .maconnerie import CalculMaconnerie
from .enduits import CalculEnduits


class AvantMetreProjet:
    """Assemble tous les calculs d'avant-métré pour un projet donné."""

    def __init__(self, nom_projet: str,
                 donnees_terrassement: DonneesTerrassement,
                 donnees_beton: DonneesBeton,
                 donnees_agglos: DonneesAgglos,
                 donnees_enduits: DonneesEnduits):
        self.nom_projet = nom_projet

        # On instancie chaque calculateur, dans le même ordre que le fichier Excel.
        self.terrassement = CalculTerrassement(donnees_terrassement)
        self.beton = CalculBeton(donnees_terrassement, donnees_beton)
        self.maconnerie = CalculMaconnerie(donnees_terrassement, donnees_agglos)

        # Enduits recalcule Sme et Sm de façon indépendante (voir enduits.py),
        # donc plus besoin de lui transmettre le résultat de maconnerie ici.
        self.enduits = CalculEnduits(donnees_enduits)

    def volume_remblai_provenant_des_fouilles(self) -> float:
        """Vrpf = Vf - (Vbp + Vbf + Vmse).
        C'est la quantité qui a besoin à la fois de Terrassement et de Béton,
        donc elle ne peut pas vivre dans un seul des deux modules."""
        vf = self.terrassement.volume_fouilles()
        vbp = self.beton.volume_beton_proprete()
        vbf = self.beton.volume_beton_fondation()
        vmse = self.terrassement.volume_mur_sous_bassement_enterre()
        return vf - (vbp + vbf + vmse)

    def resume_complet(self) -> dict:
        """Regroupe toutes les quantités du projet, section par section."""
        resultats = {}
        resultats.update(self.terrassement.resume())
        resultats["Vrpf"] = self.volume_remblai_provenant_des_fouilles()
        resultats.update(self.beton.resume())
        resultats.update(self.maconnerie.resume())
        resultats.update(self.enduits.resume())
        return resultats

    def tableau(self) -> str:
        """Génère un tableau récapitulatif texte, organisé par section."""
        lignes = []
        titre = f"AVANT-METRE — {self.nom_projet}"
        lignes.append(titre)
        lignes.append("=" * len(titre))

        sections = [
            ("TERRASSEMENT", {
                "Vf (volume fouilles)": self.terrassement.volume_fouilles(),
                "Vrpf (remblai provenant des fouilles)": self.volume_remblai_provenant_des_fouilles(),
                "Vrtal (remblai apport locaux)": self.terrassement.volume_remblai_apport_locaux(),
                "Vrtac (remblai apport cour)": self.terrassement.volume_remblai_apport_cour(),
            }),
            ("BETON", {
                "Vbp (beton proprete)": self.beton.volume_beton_proprete(),
                "Vbf (beton fondation)": self.beton.volume_beton_fondation(),
                "Vbfd (beton forme dallage)": self.beton.volume_forme_dallage(),
                "Vpa (poteaux amorces)": self.beton.volume_poteaux_amorces(),
                "Vbst (beton structure)": self.beton.volume_beton_structure(),
                "Vbdp (dalle pleine placard/cuisine)": self.beton.volume_dalle_pleine_placard_cuisine(),
            }),
            ("MACONNERIE - AGGLOS", {
                "Smsb (surface mur soubassement)": self.maconnerie.surface_mur_soubassement(),
                "Sme (surface mur elevation)": self.maconnerie.surface_mur_elevation(),
            }),
            ("ENDUITS", {
                "EnV (enduit vertical)": self.enduits.surface_enduit_vertical(),
                "EnH (enduit horizontal)": self.enduits.surface_enduit_horizontal(),
            }),
        ]

        for nom_section, valeurs in sections:
            lignes.append("")
            lignes.append(f"-- {nom_section} --")
            for label, valeur in valeurs.items():
                lignes.append(f"  {label:<42} {valeur:>10.3f}")

        return "\n".join(lignes)
