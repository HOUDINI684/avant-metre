"""
Tests du calcul détaillé des armatures (armature.py).

Chaque test vérifie une formule à la main (valeurs choisies pour être
faciles à recalculer au brouillon), dans l'esprit des autres fichiers de
tests du projet.
"""

from avant_metre.donnees import (
    DonneesBeton, SectionSemelleFilante, SectionSemelleIsolee,
    SectionPoteau, SectionPoutre, SectionLongrine, DonneesArmaturesDetaillees,
    FerraillageLineaire, FerraillageSemelleFilante, FerraillageSemelleIsolee,
)
from avant_metre.armature import CalculArmature


def _armature_par_defaut():
    return DonneesArmaturesDetaillees(
        semelle_filante=FerraillageSemelleFilante(
            nb_barres_longitudinales=3, diametre_longitudinal_mm=6,
            diametre_repartition_mm=8, espacement_repartition_cm=25.0),
        semelle_isolee=FerraillageSemelleIsolee(diametre_mm=10, espacement_cm=20.0),
        poteaux=FerraillageLineaire(nb_barres_longitudinales=4, diametre_longitudinal_mm=12,
                                     diametre_cadre_mm=6, espacement_cadre_cm=20.0),
        poutres=FerraillageLineaire(nb_barres_longitudinales=4, diametre_longitudinal_mm=12,
                                     diametre_cadre_mm=6, espacement_cadre_cm=20.0),
        longrines=FerraillageLineaire(nb_barres_longitudinales=4, diametre_longitudinal_mm=10,
                                       diametre_cadre_mm=6, espacement_cadre_cm=20.0),
        chainages=FerraillageLineaire(nb_barres_longitudinales=4, diametre_longitudinal_mm=10,
                                       diametre_cadre_mm=6, espacement_cadre_cm=20.0,
                                       cote_a=0.15, cote_b=0.15),
        enrobage_fondation_cm=5.0, enrobage_elevation_cm=2.5,
        coefficient_recouvrement_diametre=50.0,
    )


def test_recouvrement_ha6():
    """Recouvrement = coefficient x diametre. 50 x 6mm = 0.3 m."""
    db = DonneesBeton(epaisseur_beton_proprete=0)
    ca = CalculArmature(db, _armature_par_defaut())
    assert ca.recouvrement(6) == 0.3


def test_longueur_avec_recouvrement_sans_jonction():
    """Élément plus court qu'une barre commerciale (11.6m) : pas de
    jonction, donc pas de recouvrement ajouté."""
    db = DonneesBeton(epaisseur_beton_proprete=0)
    ca = CalculArmature(db, _armature_par_defaut())
    assert ca.longueur_avec_recouvrement(10.0, 12) == 10.0


def test_longueur_avec_recouvrement_avec_jonction():
    """20m de long, barre commerciale 11.6m -> 1 jonction nécessaire.
    Recouvrement HA6 = 0.3m -> longueur réelle = 20 + 0.3 = 20.3 m."""
    db = DonneesBeton(epaisseur_beton_proprete=0)
    ca = CalculArmature(db, _armature_par_defaut())
    assert round(ca.longueur_avec_recouvrement(20.0, 6), 4) == 20.3


def test_nb_barres_commerciales_arrondi_superieur():
    """25 m de fer -> 25/11.6 = 2.155... -> arrondi à 3 barres."""
    db = DonneesBeton(epaisseur_beton_proprete=0)
    ca = CalculArmature(db, _armature_par_defaut())
    assert ca.nb_barres_commerciales(25.0) == 3
    assert ca.nb_barres_commerciales(0.0) == 0


def test_perimetre_cadre():
    """Section 0.2 x 0.2, enrobage 2.5cm -> côtés utiles 0.15 x 0.15.
    Périmètre = 2*(0.15+0.15) + 0.20 (crochets) = 0.80 m."""
    db = DonneesBeton(epaisseur_beton_proprete=0)
    ca = CalculArmature(db, _armature_par_defaut())
    assert round(ca.perimetre_cadre(0.2, 0.2, 2.5), 4) == 0.80


def test_nb_cadres():
    """Longueur 3m, espacement 20cm -> floor(3/0.2)+1 = 16."""
    db = DonneesBeton(epaisseur_beton_proprete=0)
    ca = CalculArmature(db, _armature_par_defaut())
    assert ca.nb_cadres(3.0, 20.0) == 16
    assert ca.nb_cadres(0.0, 20.0) == 0


def test_semelle_filante_longitudinal():
    """20m de semelle filante, 3 barres HA6, 1 jonction (recouvrement
    0.3m) -> (20 + 0.3) * 3 = 60.9 m."""
    db = DonneesBeton(
        epaisseur_beton_proprete=0,
        semelles_filantes=[SectionSemelleFilante(longueur=20.0, largeur=0.4, epaisseur=0.2)],
    )
    ca = CalculArmature(db, _armature_par_defaut())
    assert round(ca.semelle_filante_longitudinal_m(), 2) == 60.90


def test_semelle_filante_repartition():
    """20m de long, espacement répartition 25cm -> 81 barres.
    Largeur 0.4m, enrobage fondation 5cm -> longueur utile 0.3m.
    Total = 81 * 0.3 = 24.3 m."""
    db = DonneesBeton(
        epaisseur_beton_proprete=0,
        semelles_filantes=[SectionSemelleFilante(longueur=20.0, largeur=0.4, epaisseur=0.2)],
    )
    ca = CalculArmature(db, _armature_par_defaut())
    assert round(ca.semelle_filante_repartition_m(), 2) == 24.30


def test_semelle_isolee_quadrillage_carree():
    """Semelle carrée 1x1m, espacement 20cm -> 6 barres/direction.
    Longueur utile = 1.0 - 2*0.05 = 0.9m. Total/semelle = 2*6*0.9=10.8.
    2 semelles identiques -> 21.6 m."""
    db = DonneesBeton(
        epaisseur_beton_proprete=0,
        semelles_isolees=[SectionSemelleIsolee(surface=1.0, nombre=2, epaisseur=0.3,
                                                cote_x=1.0, cote_y=1.0)],
    )
    ca = CalculArmature(db, _armature_par_defaut())
    assert round(ca.semelle_isolee_quadrillage_m(), 2) == 21.60


def test_semelle_isolee_fallback_carre_sans_cotes():
    """Si cote_x/cote_y ne sont pas fournis, on déduit un côté carré
    depuis la surface (surface=4 -> côté=2)."""
    db = DonneesBeton(
        epaisseur_beton_proprete=0,
        semelles_isolees=[SectionSemelleIsolee(surface=4.0, nombre=1, epaisseur=0.3)],
    )
    ca = CalculArmature(db, _armature_par_defaut())
    # nb par direction = floor(2/0.2)+1 = 11 ; longueur utile = 2-0.1=1.9
    # total = 2*11*1.9 = 41.8
    assert round(ca.semelle_isolee_quadrillage_m(), 2) == 41.80


def test_poteaux_longitudinal():
    """Hauteur 3m (pas de jonction), 4 barres HA12, 2 poteaux
    identiques -> 3 * 4 * 2 = 24 m."""
    db = DonneesBeton(
        epaisseur_beton_proprete=0,
        hauteur_poteaux=3.0,
        poteaux=[SectionPoteau(section=0.04, nombre=2, cote_a=0.2, cote_b=0.2)],
    )
    ca = CalculArmature(db, _armature_par_defaut())
    assert round(ca.poteaux_longitudinal_m(), 2) == 24.00


def test_poteaux_cadres():
    """16 cadres/poteau (voir test_nb_cadres), périmètre 0.8m/cadre
    (voir test_perimetre_cadre), 2 poteaux -> 16*0.8*2 = 25.6 m."""
    db = DonneesBeton(
        epaisseur_beton_proprete=0,
        hauteur_poteaux=3.0,
        poteaux=[SectionPoteau(section=0.04, nombre=2, cote_a=0.2, cote_b=0.2)],
    )
    ca = CalculArmature(db, _armature_par_defaut())
    assert round(ca.poteaux_cadres_m(), 2) == 25.60


def test_poteaux_fallback_carre_sans_cotes():
    """Sans cote_a/cote_b, on déduit un côté carré depuis la section
    (section=0.04 -> côté=0.2), donc même résultat que le test précédent."""
    db = DonneesBeton(
        epaisseur_beton_proprete=0,
        hauteur_poteaux=3.0,
        poteaux=[SectionPoteau(section=0.04, nombre=2)],
    )
    ca = CalculArmature(db, _armature_par_defaut())
    assert round(ca.poteaux_cadres_m(), 2) == 25.60


def test_poutres_longitudinal_et_cadres():
    """Poutre de 5m, section 0.2x0.3 (largeur/hauteur fournies), 4 HA12,
    espacement cadre 20cm."""
    db = DonneesBeton(
        epaisseur_beton_proprete=0,
        poutres=[SectionPoutre(section=0.06, longueur=5.0, largeur=0.2, hauteur=0.3)],
    )
    ca = CalculArmature(db, _armature_par_defaut())
    # longitudinal : 5m (pas de jonction) * 4 barres = 20 m
    assert round(ca.poutres_longitudinal_m(), 2) == 20.00
    # cadres : nb = floor(5/0.2)+1 = 26 ; perimetre = 2*((0.2-0.05)+(0.3-0.05))+0.2 = 0.2+0.8=1.0
    assert round(ca.poutres_cadres_m(), 2) == 26.00


def test_longrines_vide_par_defaut():
    """Aucune longrine définie -> 0 partout, pas d'erreur."""
    db = DonneesBeton(epaisseur_beton_proprete=0, longrines=[])
    ca = CalculArmature(db, _armature_par_defaut())
    assert ca.longrines_longitudinal_m() == 0.0
    assert ca.longrines_cadres_m() == 0.0


def test_chainage():
    """20m de chaînage, section 0.15x0.15, 4 barres HA10, espacement
    cadre 20cm."""
    db = DonneesBeton(epaisseur_beton_proprete=0, longueur_developpee_chainage=20.0)
    ca = CalculArmature(db, _armature_par_defaut())
    # longitudinal : 1 jonction (20 > 11.6), recouvrement HA10 = 50*0.010=0.5
    # -> (20 + 0.5) * 4 = 82 m
    assert round(ca.chainage_longitudinal_m(), 2) == 82.00
    # cadres : nb = floor(20/0.2)+1 = 101 ; perimetre = 2*(0.1+0.1)+0.2 = 0.6
    assert round(ca.chainage_cadres_m(), 2) == 60.60


def test_dalle_pleine_quadrillage():
    """Placard 2x1.5m, espacement 20cm. Paillasse cuisine non définie
    (0x0) -> ignorée."""
    db = DonneesBeton(
        epaisseur_beton_proprete=0,
        longueur_placard=2.0, largeur_placard=1.5, epaisseur_dalle_pleine=0.1,
    )
    ca = CalculArmature(db, _armature_par_defaut())
    # dir x (le long de 1.5m, espacée sur 1.5) : nb=floor(1.5/0.2)+1=8, longueur utile=2-0.05=1.95
    # dir y (le long de 2m, espacée sur 2) : nb=floor(2/0.2)+1=11, longueur utile=1.5-0.05=1.45
    # total = 8*1.95 + 11*1.45 = 15.6 + 15.95 = 31.55
    assert round(ca.dalle_pleine_quadrillage_m(), 2) == 31.55


def test_escalier_absent():
    """Pas d'escalier défini -> estimation à 0, pas d'erreur."""
    db = DonneesBeton(epaisseur_beton_proprete=0, escalier=None)
    ca = CalculArmature(db, _armature_par_defaut())
    assert ca.escalier_surface_paillasse_m2() == 0.0
    assert ca.escalier_poids_treillis_kg() == 0.0


def test_barres_par_diametre_regroupe_les_memes_diametres():
    """Semelle filante longitudinal (HA6) et cadres poteaux (HA6, si
    même diamètre choisi) doivent se cumuler dans la même entrée."""
    da = _armature_par_defaut()
    da.poteaux.diametre_cadre_mm = 6  # même diamètre que le HA6 des semelles
    db = DonneesBeton(
        epaisseur_beton_proprete=0,
        semelles_filantes=[SectionSemelleFilante(longueur=10.0, largeur=0.4, epaisseur=0.2)],
        hauteur_poteaux=3.0,
        poteaux=[SectionPoteau(section=0.04, nombre=1, cote_a=0.2, cote_b=0.2)],
    )
    ca = CalculArmature(db, da)
    resultat = ca.barres_par_diametre()
    assert 6 in resultat
    # la longueur cumulée doit être strictement supérieure à la seule
    # contribution des semelles (preuve que les 2 sources sont additionnées)
    assert resultat[6]["longueur_totale_m"] > ca.semelle_filante_longitudinal_m()


def test_resume_contient_toutes_les_sections():
    db = DonneesBeton(epaisseur_beton_proprete=0)
    ca = CalculArmature(db, _armature_par_defaut())
    r = ca.resume()
    for cle in ("semelle_filante", "semelle_isolee", "poteaux", "poutres",
                "longrines", "chainages", "dalle_pleine", "escalier_estimation",
                "barres_par_diametre"):
        assert cle in r
