"""
devis.py
========
Calcul des quantités de matériaux (ciment, sable, gravier, agglos, acier)
à partir des volumes et surfaces déjà calculés par les autres modules,
en utilisant les dosages définis dans dosages.py.

Ce module ne connaît aucune géométrie : il prend un dictionnaire de
résultats (volumes en m3, surfaces en m2) et des longueurs d'armatures,
puis applique des ratios. C'est ce qui permet de changer les dosages
sans jamais toucher aux calculs de volumes.
"""

import math

from . import dosages
from .donnees import DonneesArmatures


class CalculDevis:
    """Calcule les quantités de matériaux à partir des résultats de l'avant-métré."""

    def __init__(self, resultats: dict, donnees_armatures: DonneesArmatures = None):
        """
        resultats : dict produit par AvantMetreProjet.resume_complet(),
        contenant au moins Vbp, Vbf, Vbfd, Vbst, Vbdp, Vpa, Smsb, Sme.

        donnees_armatures : longueurs développées d'armatures des semelles,
        pour le calcul de l'acier en nombre de barres (comme le fichier
        de référence). Optionnel : si absent, ces quantités valent 0.
        """
        self.resultats = resultats
        self.da = donnees_armatures or DonneesArmatures()

    # ------------------------------------------------------------------
    # Ciment
    # ------------------------------------------------------------------

    def quantite_ciment_kg(self) -> dict:
        """Poids de ciment (kg) nécessaire, détaillé par type de béton."""
        detail = {}
        for cle_volume, dosage in dosages.DOSAGE_CIMENT_KG_PAR_M3.items():
            volume = self.resultats.get(cle_volume, 0.0)
            detail[cle_volume] = volume * dosage
        return detail

    def quantite_ciment_sacs(self) -> dict:
        """Nombre de sacs de ciment, détaillé par type de béton."""
        return {cle: math.ceil(kg / dosages.POIDS_SAC_CIMENT_KG)
                for cle, kg in self.quantite_ciment_kg().items()}

    def total_ciment_sacs(self) -> float:
        """Nombre total de sacs de ciment, tous types de béton confondus."""
        return sum(self.quantite_ciment_sacs().values())

    # ------------------------------------------------------------------
    # Sable et gravier
    # ------------------------------------------------------------------

    def volume_total_beton(self) -> float:
        """Somme de tous les volumes de béton du projet."""
        cles_beton = dosages.DOSAGE_CIMENT_KG_PAR_M3.keys()
        return sum(self.resultats.get(cle, 0.0) for cle in cles_beton)

    def quantite_sable_m3(self) -> float:
        return self.volume_total_beton() * dosages.VOLUME_SABLE_PAR_M3_BETON

    def quantite_gravier_m3(self) -> float:
        return self.volume_total_beton() * dosages.VOLUME_GRAVIER_PAR_M3_BETON

    # ------------------------------------------------------------------
    # Agglos (achat, moulage, jointement)
    # ------------------------------------------------------------------

    def quantite_agglos(self) -> int:
        """Nombre d'agglos (parpaings), à partir des surfaces de murs."""
        surface_totale = self.resultats.get("Smsb", 0.0) + self.resultats.get("Sme", 0.0)
        return math.ceil(surface_totale * dosages.NB_AGGLOS_PAR_M2)

    def ciment_moulage_agglos_sacs(self) -> int:
        """Si les agglos sont fabriqués sur place plutôt qu'achetés :
        sacs de ciment nécessaires pour les mouler."""
        return math.ceil(self.quantite_agglos() / dosages.NB_AGGLOS_PAR_SAC_CIMENT)

    def sable_moulage_agglos_m3(self) -> float:
        return self.ciment_moulage_agglos_sacs() * dosages.RATIO_SABLE_MOULAGE_AGGLOS

    def ciment_jointement_mur_sacs(self) -> int:
        """Ciment pour le mortier de pose (jointement) des agglos."""
        surface_totale = self.resultats.get("Smsb", 0.0) + self.resultats.get("Sme", 0.0)
        kg = surface_totale * dosages.CIMENT_KG_PAR_M2_JOINTEMENT
        return math.ceil(kg / dosages.POIDS_SAC_CIMENT_KG)

    def sable_jointement_mur_m3(self) -> float:
        return self.ciment_jointement_mur_sacs() * dosages.RATIO_SABLE_JOINTEMENT

    # ------------------------------------------------------------------
    # Acier des semelles : nombre de barres commerciales, par diamètre
    # ------------------------------------------------------------------

    def nombre_barres_ha6(self) -> int:
        """HA6 : armature longitudinale de la semelle filante."""
        ld = self.da.longueur_ha6_longitudinal_semelle_filante
        longueur_totale = ld * dosages.NB_BARRES_LONGITUDINALES_PAR_SEMELLE_FILANTE
        return math.ceil(longueur_totale / dosages.LONGUEUR_BARRE_COMMERCIALE_M)

    def nombre_barres_ha8(self) -> int:
        """HA8 : armature transversale (cadres/étriers) de la semelle filante."""
        ld = self.da.longueur_ha8_transversal_semelle_filante
        return math.ceil(ld / dosages.LONGUEUR_BARRE_COMMERCIALE_M)

    def nombre_barres_ha10(self) -> int:
        """HA10 : armature des semelles isolées."""
        ld = self.da.longueur_ha10_semelles_isolees
        return math.ceil(ld / dosages.LONGUEUR_BARRE_COMMERCIALE_M)

    def detail_barres_semelles(self) -> dict:
        """Nombre de barres commerciales nécessaires, par diamètre."""
        return {
            "HA6 (longitudinal semelle filante)": self.nombre_barres_ha6(),
            "HA8 (transversal semelle filante)": self.nombre_barres_ha8(),
            "HA10 (semelles isolées)": self.nombre_barres_ha10(),
        }

    def poids_indicatif_barres_semelles_kg(self) -> float:
        """Poids total indicatif de l'acier des semelles, à partir du
        nombre de barres et du poids linéaire standard par diamètre."""
        p = dosages.POIDS_LINEAIRE_ACIER_KG_PAR_M
        l = dosages.LONGUEUR_BARRE_COMMERCIALE_M
        return (self.nombre_barres_ha6() * l * p["HA6"]
                + self.nombre_barres_ha8() * l * p["HA8"]
                + self.nombre_barres_ha10() * l * p["HA10"])

    # ------------------------------------------------------------------
    # Acier du reste de la structure (ratio kg/m3, faute de détail dans
    # le fichier de référence pour poteaux/poutres/chaînages/escalier)
    # ------------------------------------------------------------------

    def poids_acier_structure_kg(self) -> dict:
        detail = {}
        for cle_volume, ratio in dosages.RATIO_ACIER_KG_PAR_M3.items():
            volume = self.resultats.get(cle_volume, 0.0)
            detail[cle_volume] = volume * ratio
        return detail

    def total_acier_structure_kg(self) -> float:
        return sum(self.poids_acier_structure_kg().values())

    # ------------------------------------------------------------------
    # Résumé
    # ------------------------------------------------------------------

    def tableau(self) -> str:
        lignes = []
        lignes.append("DEVIS QUANTITATIF DE MATERIAUX")
        lignes.append("=" * 34)

        lignes.append("")
        lignes.append("-- CIMENT (sacs de 50 kg) --")
        for cle, sacs in self.quantite_ciment_sacs().items():
            lignes.append(f"  {cle:<10} {sacs:>10} sacs")
        lignes.append(f"  {'TOTAL':<10} {self.total_ciment_sacs():>10} sacs")

        lignes.append("")
        lignes.append("-- GRANULATS (beton) --")
        lignes.append(f"  Sable    {self.quantite_sable_m3():>10.2f} m3")
        lignes.append(f"  Gravier  {self.quantite_gravier_m3():>10.2f} m3")

        lignes.append("")
        lignes.append("-- AGGLOS --")
        lignes.append(f"  Agglos                  {self.quantite_agglos():>10} unites")
        lignes.append(f"  Ciment moulage agglos    {self.ciment_moulage_agglos_sacs():>10} sacs")
        lignes.append(f"  Sable moulage agglos     {self.sable_moulage_agglos_m3():>10.2f} m3")
        lignes.append(f"  Ciment jointement mur    {self.ciment_jointement_mur_sacs():>10} sacs")
        lignes.append(f"  Sable jointement mur     {self.sable_jointement_mur_m3():>10.2f} m3")

        lignes.append("")
        lignes.append("-- ACIER DES SEMELLES (nombre de barres, 11.6 m) --")
        for cle, nb in self.detail_barres_semelles().items():
            lignes.append(f"  {cle:<38} {nb:>6} barres")
        lignes.append(f"  Poids indicatif total          {self.poids_indicatif_barres_semelles_kg():>10.1f} kg")

        lignes.append("")
        lignes.append("-- ACIER DE LA STRUCTURE (ratio kg/m3, estimation) --")
        for cle, kg in self.poids_acier_structure_kg().items():
            lignes.append(f"  {cle:<10} {kg:>10.1f} kg")
        lignes.append(f"  {'TOTAL':<10} {self.total_acier_structure_kg():>10.1f} kg")

        return "\n".join(lignes)
