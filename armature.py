"""
armature.py
===========
Calcul détaillé des armatures (acier béton armé) pour l'ensemble des
éléments de gros œuvre : semelles filantes, semelles isolées, poteaux,
poutres, longrines, chaînages, dalle pleine.

Contrairement à l'approche existante dans devis.py (qui convertit des
longueurs de fer déjà calculées en amont), ce module calcule lui-même
les longueurs à partir des règles de ferraillage (nombre de barres,
diamètre, espacement) et de la géométrie déjà saisie dans DonneesBeton,
en tenant compte :
    - des recouvrements aux jonctions entre barres commerciales (11,6 m)
    - de l'enrobage (le cadre est en retrait par rapport au bord du béton)
    - de l'espacement réel des cadres/étriers ou des barres de répartition

Principe pour un élément linéaire (poteau, poutre, longrine, chaînage) :
    armature longitudinale :
        longueur réelle de fer = longueur de l'élément
                                  + (nb_jonctions x recouvrement)
        longueur totale acier  = longueur réelle x nb_barres_longitudinales
    cadres/étriers :
        nb_cadres  = longueur élément / espacement + 1
        long_cadre = 2 x (cote_a + cote_b - 4 x enrobage) + crochets

Toutes les longueurs d'acier sont ensuite ramenées en nombre de barres
commerciales de 11,6 m (arrondi supérieur), par diamètre — on ne peut
pas commander une fraction de barre.

Limite assumée : l'escalier n'est pas couvert par un calcul détaillé
(sa géométrie en pente ne se prête pas à une formule simple sans plan de
ferraillage dédié) ; il reste estimé par un ratio de treillis soudé.
"""

import math

from .donnees import DonneesBeton, DonneesArmaturesDetaillees
from . import dosages


LONGUEUR_CROCHET_FORFAITAIRE_M = 0.20  # 2 crochets x 0.10 m, valeur usuelle


class CalculArmature:
    """Calcule le ferraillage détaillé de tout le gros œuvre à partir de
    la géométrie béton (DonneesBeton) et des paramètres de ferraillage
    (DonneesArmaturesDetaillees)."""

    def __init__(self, donnees_beton: DonneesBeton, donnees_armatures: DonneesArmaturesDetaillees):
        self.db = donnees_beton
        self.da = donnees_armatures

    # ------------------------------------------------------------------
    # Utilitaires génériques (partagés par tous les éléments)
    # ------------------------------------------------------------------

    def recouvrement(self, diametre_mm: float) -> float:
        """Longueur de recouvrement à chaque jonction de barre, en m.
        Règle usuelle : coefficient x diamètre (50 x Ø par défaut)."""
        return self.da.coefficient_recouvrement_diametre * diametre_mm / 1000

    def longueur_avec_recouvrement(self, longueur_element: float, diametre_mm: float) -> float:
        """Longueur réelle de fer nécessaire pour qu'UNE barre filante
        coure sur toute la longueur d'un élément, recouvrements compris
        à chaque jonction entre barres commerciales de 11,6 m."""
        if longueur_element <= 0:
            return 0.0
        barre = dosages.LONGUEUR_BARRE_COMMERCIALE_M
        nb_jonctions = max(0, math.ceil(longueur_element / barre) - 1)
        return longueur_element + nb_jonctions * self.recouvrement(diametre_mm)

    @staticmethod
    def nb_barres_commerciales(longueur_totale_m: float) -> int:
        """Convertit une longueur totale d'acier en nombre de barres
        commerciales de 11,6 m (arrondi supérieur : on ne peut pas
        acheter une fraction de barre)."""
        if longueur_totale_m <= 0:
            return 0
        return math.ceil(longueur_totale_m / dosages.LONGUEUR_BARRE_COMMERCIALE_M)

    @staticmethod
    def perimetre_cadre(cote_a: float, cote_b: float, enrobage_cm: float) -> float:
        """Longueur développée d'un cadre/étrier rectangulaire, en tenant
        compte de l'enrobage (le cadre est à l'intérieur de la section,
        en retrait de l'enrobage sur chaque face) + majoration forfaitaire
        pour les 2 crochets de recouvrement du cadre."""
        e = enrobage_cm / 100
        a = max(cote_a - 2 * e, 0.0)
        b = max(cote_b - 2 * e, 0.0)
        return 2 * (a + b) + LONGUEUR_CROCHET_FORFAITAIRE_M

    @staticmethod
    def nb_cadres(longueur_element: float, espacement_cm: float) -> int:
        """Nombre de cadres/étriers (ou de barres de répartition) sur la
        longueur d'un élément, espacement donné en cm."""
        if longueur_element <= 0 or espacement_cm <= 0:
            return 0
        return math.floor(longueur_element / (espacement_cm / 100)) + 1

    @staticmethod
    def _cote_carre_equivalent(surface_ou_section: float) -> float:
        """Dimension d'un côté, si on suppose une section/semelle carrée
        de surface donnée (fallback quand cote_a/cote_b ne sont pas
        renseignés)."""
        return math.sqrt(surface_ou_section) if surface_ou_section > 0 else 0.0

    # ------------------------------------------------------------------
    # Semelles filantes
    # ------------------------------------------------------------------

    def semelle_filante_longitudinal_m(self) -> float:
        """Longueur totale d'acier longitudinal (toutes semelles filantes
        confondues)."""
        f = self.da.semelle_filante
        total = 0.0
        for s in self.db.semelles_filantes:
            long_barre = self.longueur_avec_recouvrement(s.longueur, f.diametre_longitudinal_mm)
            total += long_barre * f.nb_barres_longitudinales
        return total

    def semelle_filante_repartition_m(self) -> float:
        """Longueur totale d'acier de répartition (transversal) pour
        toutes les semelles filantes."""
        f = self.da.semelle_filante
        enrobage = self.da.enrobage_fondation_cm
        total = 0.0
        for s in self.db.semelles_filantes:
            nb = self.nb_cadres(s.longueur, f.espacement_repartition_cm)
            longueur_unitaire = max(s.largeur - 2 * enrobage / 100, 0.0)
            total += nb * longueur_unitaire
        return total

    # ------------------------------------------------------------------
    # Semelles isolées
    # ------------------------------------------------------------------

    def semelle_isolee_quadrillage_m(self) -> float:
        """Longueur totale d'acier de la nappe inférieure (2 directions)
        pour toutes les semelles isolées."""
        f = self.da.semelle_isolee
        enrobage = self.da.enrobage_fondation_cm / 100
        total = 0.0
        for s in self.db.semelles_isolees:
            cx = s.cote_x or self._cote_carre_equivalent(s.surface)
            cy = s.cote_y or self._cote_carre_equivalent(s.surface)
            nb_barres_dir_x = self.nb_cadres(cy, f.espacement_cm)
            nb_barres_dir_y = self.nb_cadres(cx, f.espacement_cm)
            longueur_par_semelle = (nb_barres_dir_x * max(cx - 2 * enrobage, 0.0)
                                     + nb_barres_dir_y * max(cy - 2 * enrobage, 0.0))
            total += longueur_par_semelle * s.nombre
        return total

    # ------------------------------------------------------------------
    # Éléments linéaires génériques : poteaux, poutres, longrines
    # ------------------------------------------------------------------

    def _lineaire_liste(self, elements, longueur_attr, cote_a_attr, cote_b_attr,
                         nombre_attr, ferr, enrobage_cm) -> tuple:
        """Calcule (longueur_totale_longitudinal_m, longueur_totale_cadres_m)
        pour une liste d'éléments (poteaux, poutres ou longrines), en
        appliquant les mêmes paramètres de ferraillage `ferr` à tous les
        éléments de la liste (simplification : un seul jeu de paramètres
        par type d'élément, pas par sous-type)."""
        total_long = 0.0
        total_cadres = 0.0
        for el in elements:
            longueur = getattr(el, longueur_attr)
            nombre = getattr(el, nombre_attr) if nombre_attr else 1
            section = getattr(el, "section", 0.0)
            cote_a = getattr(el, cote_a_attr) or self._cote_carre_equivalent(section)
            cote_b = getattr(el, cote_b_attr) or self._cote_carre_equivalent(section)

            long_barre = self.longueur_avec_recouvrement(longueur, ferr.diametre_longitudinal_mm)
            total_long += long_barre * ferr.nb_barres_longitudinales * nombre

            nb_c = self.nb_cadres(longueur, ferr.espacement_cadre_cm)
            long_cadre = self.perimetre_cadre(cote_a, cote_b, enrobage_cm)
            total_cadres += nb_c * long_cadre * nombre
        return total_long, total_cadres

    def poteaux_longitudinal_m(self) -> float:
        # Les poteaux stockent un "nombre" (multiplicité) mais une hauteur
        # commune (db.hauteur_poteaux), pas une longueur propre par item.
        f = self.da.poteaux
        total = 0.0
        for p in self.db.poteaux:
            long_barre = self.longueur_avec_recouvrement(self.db.hauteur_poteaux, f.diametre_longitudinal_mm)
            total += long_barre * f.nb_barres_longitudinales * p.nombre
        return total

    def poteaux_cadres_m(self) -> float:
        f = self.da.poteaux
        enrobage = self.da.enrobage_elevation_cm
        total = 0.0
        for p in self.db.poteaux:
            cote_a = p.cote_a or self._cote_carre_equivalent(p.section)
            cote_b = p.cote_b or self._cote_carre_equivalent(p.section)
            nb_c = self.nb_cadres(self.db.hauteur_poteaux, f.espacement_cadre_cm)
            long_cadre = self.perimetre_cadre(cote_a, cote_b, enrobage)
            total += nb_c * long_cadre * p.nombre
        return total

    def poutres_longitudinal_m(self) -> float:
        total, _ = self._lineaire_liste(
            self.db.poutres, "longueur", "largeur", "hauteur", None,
            self.da.poutres, self.da.enrobage_elevation_cm)
        return total

    def poutres_cadres_m(self) -> float:
        _, total = self._lineaire_liste(
            self.db.poutres, "longueur", "largeur", "hauteur", None,
            self.da.poutres, self.da.enrobage_elevation_cm)
        return total

    def longrines_longitudinal_m(self) -> float:
        total, _ = self._lineaire_liste(
            self.db.longrines, "longueur", "largeur", "hauteur", None,
            self.da.longrines, self.da.enrobage_elevation_cm)
        return total

    def longrines_cadres_m(self) -> float:
        _, total = self._lineaire_liste(
            self.db.longrines, "longueur", "largeur", "hauteur", None,
            self.da.longrines, self.da.enrobage_elevation_cm)
        return total

    # ------------------------------------------------------------------
    # Chaînages (un seul élément agrégé dans DonneesBeton, pas une liste)
    # ------------------------------------------------------------------

    def chainage_longitudinal_m(self) -> float:
        f = self.da.chainages
        long_barre = self.longueur_avec_recouvrement(
            self.db.longueur_developpee_chainage, f.diametre_longitudinal_mm)
        return long_barre * f.nb_barres_longitudinales

    def chainage_cadres_m(self) -> float:
        f = self.da.chainages
        nb_c = self.nb_cadres(self.db.longueur_developpee_chainage, f.espacement_cadre_cm)
        long_cadre = self.perimetre_cadre(f.cote_a, f.cote_b, self.da.enrobage_elevation_cm)
        return nb_c * long_cadre

    # ------------------------------------------------------------------
    # Dalle pleine (placard + paillasse cuisine)
    # ------------------------------------------------------------------

    def dalle_pleine_quadrillage_m(self) -> float:
        f = self.da.dalle_pleine
        enrobage = self.da.enrobage_elevation_cm / 100
        total = 0.0
        for longueur, largeur in (
            (self.db.longueur_placard, self.db.largeur_placard),
            (self.db.longueur_paillasse_cuisine, self.db.largeur_paillasse_cuisine),
        ):
            if longueur <= 0 or largeur <= 0:
                continue
            nb_dir_x = self.nb_cadres(largeur, f.espacement_cm)
            nb_dir_y = self.nb_cadres(longueur, f.espacement_cm)
            total += (nb_dir_x * max(longueur - 2 * enrobage, 0.0)
                      + nb_dir_y * max(largeur - 2 * enrobage, 0.0))
        return total

    # ------------------------------------------------------------------
    # Escalier — estimation (voir limite documentée en tête de fichier)
    # ------------------------------------------------------------------

    def escalier_surface_paillasse_m2(self) -> float:
        esc = self.db.escalier
        if esc is None:
            return 0.0
        return esc.longueur_paillasse * esc.emmarchement + esc.longueur_palier * esc.largeur_palier

    def escalier_poids_treillis_kg(self) -> float:
        return self.escalier_surface_paillasse_m2() * self.da.ratio_treillis_escalier_kg_m2

    # ------------------------------------------------------------------
    # Synthèse : nombre de barres commerciales par diamètre
    # ------------------------------------------------------------------

    def barres_par_diametre(self) -> dict:
        """Regroupe TOUTES les longueurs d'acier calculées ci-dessus par
        diamètre (mm), et convertit chaque total en nombre de barres
        commerciales de 11,6 m. C'est la vue utile pour passer une
        commande groupée (les chutes d'un élément peuvent resservir sur
        un autre élément du même diamètre)."""
        longueurs_mm = {}

        def ajouter(diam_mm, longueur_m):
            longueurs_mm[diam_mm] = longueurs_mm.get(diam_mm, 0.0) + longueur_m

        ajouter(self.da.semelle_filante.diametre_longitudinal_mm, self.semelle_filante_longitudinal_m())
        ajouter(self.da.semelle_filante.diametre_repartition_mm, self.semelle_filante_repartition_m())
        ajouter(self.da.semelle_isolee.diametre_mm, self.semelle_isolee_quadrillage_m())

        ajouter(self.da.poteaux.diametre_longitudinal_mm, self.poteaux_longitudinal_m())
        ajouter(self.da.poteaux.diametre_cadre_mm, self.poteaux_cadres_m())

        ajouter(self.da.poutres.diametre_longitudinal_mm, self.poutres_longitudinal_m())
        ajouter(self.da.poutres.diametre_cadre_mm, self.poutres_cadres_m())

        ajouter(self.da.longrines.diametre_longitudinal_mm, self.longrines_longitudinal_m())
        ajouter(self.da.longrines.diametre_cadre_mm, self.longrines_cadres_m())

        ajouter(self.da.chainages.diametre_longitudinal_mm, self.chainage_longitudinal_m())
        ajouter(self.da.chainages.diametre_cadre_mm, self.chainage_cadres_m())

        ajouter(self.da.dalle_pleine.diametre_mm, self.dalle_pleine_quadrillage_m())

        return {
            diam: {
                "longueur_totale_m": round(longueur, 2),
                "nb_barres_commerciales": self.nb_barres_commerciales(longueur),
            }
            for diam, longueur in sorted(longueurs_mm.items()) if longueur > 0
        }

    def resume(self) -> dict:
        """Détail par élément + synthèse par diamètre + estimation
        escalier (traitée à part, en kg de treillis)."""
        return {
            "semelle_filante": {
                "longitudinal_m": round(self.semelle_filante_longitudinal_m(), 2),
                "repartition_m": round(self.semelle_filante_repartition_m(), 2),
            },
            "semelle_isolee": {
                "quadrillage_m": round(self.semelle_isolee_quadrillage_m(), 2),
            },
            "poteaux": {
                "longitudinal_m": round(self.poteaux_longitudinal_m(), 2),
                "cadres_m": round(self.poteaux_cadres_m(), 2),
            },
            "poutres": {
                "longitudinal_m": round(self.poutres_longitudinal_m(), 2),
                "cadres_m": round(self.poutres_cadres_m(), 2),
            },
            "longrines": {
                "longitudinal_m": round(self.longrines_longitudinal_m(), 2),
                "cadres_m": round(self.longrines_cadres_m(), 2),
            },
            "chainages": {
                "longitudinal_m": round(self.chainage_longitudinal_m(), 2),
                "cadres_m": round(self.chainage_cadres_m(), 2),
            },
            "dalle_pleine": {
                "quadrillage_m": round(self.dalle_pleine_quadrillage_m(), 2),
            },
            "escalier_estimation": {
                "surface_paillasse_m2": round(self.escalier_surface_paillasse_m2(), 2),
                "poids_treillis_kg": round(self.escalier_poids_treillis_kg(), 2),
            },
            "barres_par_diametre": self.barres_par_diametre(),
        }
