"""
beton.py
========
Calcul des quantités de béton (propreté, fondation, structure, dalles)
à partir des données saisies (DonneesBeton), en réutilisant la géométrie
des fouilles (DonneesTerrassement) pour Vbp et Vbf.

Formules principales :
    Vbp  = (Ldfr x l x epbp) + Sum(Si x ni x epbp)
    Vbf  = Sum(longueur x largeur x epaisseur) pour chaque type de semelle filante
           + Sum(surface x nombre x epaisseur) pour chaque type de semelle isolee
    Vbfd = Sum(surface x epaisseur) pour chaque zone de forme de dallage
    Vch  = section_chainage x longueur_developpee_chainage
    VPi  = Sum(section_poteau x nombre x hauteur_poteaux)
    VPPi = Sum(section_poutre x longueur)
    VLGi = Sum(section_longrine x longueur)
    Vbes = volume_marches + volume_paillasse + volume_palier
    Vbst = Vch + VPi + VPPi + VLGi + Vbes
    Vbdp = (Lpc x lpc x eppc) + (Lp x lp x eppc)
"""

from .donnees import DonneesBeton, DonneesTerrassement


class CalculBeton:
    """Calcule les quantités de béton pour un jeu de données donné."""

    def __init__(self, donnees_terrassement: DonneesTerrassement, donnees_beton: DonneesBeton):
        self.dt = donnees_terrassement
        self.db = donnees_beton

    # ------------------------------------------------------------------
    # Béton de propreté et de fondation (suivent la géométrie des fouilles)
    # ------------------------------------------------------------------

    def volume_beton_proprete(self) -> float:
        """Vbp = béton de propreté, sous rigole + sous fouilles en trous."""
        dt, db = self.dt, self.db
        terme_rigole = dt.longueur_developpee_rigole * dt.largeur_rigole * db.epaisseur_beton_proprete
        terme_trous = sum(f.surface * f.nombre * db.epaisseur_beton_proprete
                          for f in dt.fouilles_en_trous)
        return terme_rigole + terme_trous

    def volume_beton_fondation(self) -> float:
        """Vbf = béton de fondation, somme de tous les types de semelles
        filantes et de semelles isolées définis pour le projet."""
        terme_filantes = sum(s.longueur * s.largeur * s.epaisseur
                             for s in self.db.semelles_filantes)
        terme_isolees = sum(s.surface * s.nombre * s.epaisseur
                            for s in self.db.semelles_isolees)
        return terme_filantes + terme_isolees

    def volume_forme_dallage(self) -> float:
        """Vbfd = béton pour forme de dallage, somme de toutes les zones
        définies (qui peuvent avoir des épaisseurs différentes)."""
        return sum(f.surface * f.epaisseur for f in self.db.formes_dallage)

    def volume_poteaux_amorces(self) -> float:
        """Vpa = volume des poteaux amorces : tronçons de poteaux qui
        émergent des semelles avant le coulage des poteaux en élévation.
        Valeur saisie directement (le fichier de référence ne détaille
        pas de formule pour ce volume)."""
        return self.db.volume_poteaux_amorces

    # ------------------------------------------------------------------
    # Béton de structure : chaînages, poteaux, poutres, longrines, escalier
    # ------------------------------------------------------------------

    def volume_chainage(self) -> float:
        """Vch = section combinée des chaînages x longueur développée."""
        return self.db.section_chainage * self.db.longueur_developpee_chainage

    def volume_poteaux(self) -> float:
        """Somme des volumes de chaque type de poteau."""
        db = self.db
        return sum(p.section * p.nombre * db.hauteur_poteaux for p in db.poteaux)

    def volume_poutres(self) -> float:
        """Somme des volumes de chaque type de poutre."""
        return sum(p.section * p.longueur for p in self.db.poutres)

    def volume_longrines(self) -> float:
        """Somme des volumes de chaque type de longrine."""
        return sum(l.section * l.longueur for l in self.db.longrines)

    def volume_escalier(self) -> float:
        """Vbes = volume béton d'un escalier (marches + paillasse + palier).
        Retourne 0 si aucun escalier n'est défini."""
        esc = self.db.escalier
        if esc is None:
            return 0.0
        volume_marches = (esc.hauteur_marche * esc.largeur_marche / 2) * esc.emmarchement * esc.nombre_marches
        volume_paillasse = esc.longueur_paillasse * esc.epaisseur_paillasse * esc.emmarchement
        volume_palier = esc.longueur_palier * esc.largeur_palier * esc.epaisseur_paillasse
        return volume_marches + volume_paillasse + volume_palier

    def volume_beton_structure(self) -> float:
        """Vbst = total du béton de structure (chaînages + poteaux + poutres
        + longrines + escalier)."""
        return (self.volume_chainage()
                + self.volume_poteaux()
                + self.volume_poutres()
                + self.volume_longrines()
                + self.volume_escalier())

    # ------------------------------------------------------------------
    # Dalle pleine placard / paillasse cuisine
    # ------------------------------------------------------------------

    def volume_dalle_pleine_placard_cuisine(self) -> float:
        """Vbdp = dalle pleine des placards + paillasse de cuisine."""
        db = self.db
        vol_placard = db.longueur_placard * db.largeur_placard * db.epaisseur_dalle_pleine
        vol_cuisine = db.longueur_paillasse_cuisine * db.largeur_paillasse_cuisine * db.epaisseur_dalle_pleine
        return vol_placard + vol_cuisine

    def resume(self) -> dict:
        """Retourne toutes les quantités béton dans un dict."""
        return {
            "Vbp": self.volume_beton_proprete(),
            "Vbf": self.volume_beton_fondation(),
            "Vbfd": self.volume_forme_dallage(),
            "Vpa": self.volume_poteaux_amorces(),
            "Vbst": self.volume_beton_structure(),
            "Vbdp": self.volume_dalle_pleine_placard_cuisine(),
        }
