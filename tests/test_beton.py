"""
test_beton.py
=============
Tests unitaires du module beton.py.
"""

import pytest
from avant_metre.donnees import (
    DonneesTerrassement, SectionFouille,
    DonneesBeton, SectionPoteau, SectionPoutre, SectionLongrine, DonneesEscalier,
    SectionSemelleFilante, SectionSemelleIsolee, SectionFormeDallage,
)
from avant_metre.beton import CalculBeton


def _donnees_terrassement_reference():
    """Jeu de données de terrassement réutilisé par plusieurs tests béton,
    car Vbp en dépend."""
    return DonneesTerrassement(
        longueur_developpee_rigole=64.63,
        profondeur_rigole=1.3,
        largeur_rigole=0.5,
        fouilles_en_trous=[
            SectionFouille(surface=2.56, nombre=25),
            SectionFouille(surface=4.0, nombre=2),
            SectionFouille(surface=4.32, nombre=3),
        ],
        profondeur_fouille_trou=1.4,
        surface_locaux=154.82,
    )


def test_volume_beton_proprete():
    dt = _donnees_terrassement_reference()
    db = DonneesBeton(epaisseur_beton_proprete=0.05)
    calc = CalculBeton(dt, db)
    assert calc.volume_beton_proprete() == pytest.approx(5.8638, abs=0.001)


def test_volume_beton_fondation_un_seul_type():
    """Cas simple : un seul type de semelle filante et un seul type de
    semelle isolée - doit redonner la même valeur qu'avant le passage
    aux listes."""
    dt = _donnees_terrassement_reference()
    db = DonneesBeton(
        epaisseur_beton_proprete=0.05,
        semelles_filantes=[SectionSemelleFilante(longueur=64.63, largeur=0.4, epaisseur=0.2)],
        semelles_isolees=[
            SectionSemelleIsolee(surface=2.56, nombre=25, epaisseur=0.3),
            SectionSemelleIsolee(surface=4.0, nombre=2, epaisseur=0.3),
            SectionSemelleIsolee(surface=4.32, nombre=3, epaisseur=0.3),
        ],
    )
    calc = CalculBeton(dt, db)
    # (64.63*0.4*0.2) + (2.56*25+4*2+4.32*3)*0.3 = 5.1704 + 25.488
    assert calc.volume_beton_fondation() == pytest.approx(30.6584, abs=0.001)


def test_volume_beton_fondation_plusieurs_types():
    """Cas réel de la demande de l'architecte : plusieurs types de semelles
    filantes avec des épaisseurs/largeurs différentes."""
    dt = _donnees_terrassement_reference()
    db = DonneesBeton(
        epaisseur_beton_proprete=0.05,
        semelles_filantes=[
            SectionSemelleFilante(longueur=40.0, largeur=0.4, epaisseur=0.2),   # murs porteurs
            SectionSemelleFilante(longueur=24.63, largeur=0.3, epaisseur=0.15),  # cloisons
        ],
        semelles_isolees=[
            SectionSemelleIsolee(surface=2.56, nombre=25, epaisseur=0.3),
        ],
    )
    calc = CalculBeton(dt, db)
    attendu = (40.0 * 0.4 * 0.2) + (24.63 * 0.3 * 0.15) + (2.56 * 25 * 0.3)
    assert calc.volume_beton_fondation() == pytest.approx(attendu, abs=0.001)


def test_volume_beton_fondation_vide():
    """Cas limite : aucune semelle définie -> 0, pas d'erreur."""
    dt = _donnees_terrassement_reference()
    db = DonneesBeton(epaisseur_beton_proprete=0.05)
    calc = CalculBeton(dt, db)
    assert calc.volume_beton_fondation() == 0.0


def test_volume_forme_dallage_un_type():
    dt = _donnees_terrassement_reference()
    db = DonneesBeton(
        epaisseur_beton_proprete=0.05,
        formes_dallage=[SectionFormeDallage(surface=154.82, epaisseur=0.05)],
    )
    calc = CalculBeton(dt, db)
    assert calc.volume_forme_dallage() == pytest.approx(7.741, abs=0.001)


def test_volume_forme_dallage_plusieurs_zones():
    """Cas réel : épaisseurs différentes selon les zones (ex: garage vs pièces de vie)."""
    dt = _donnees_terrassement_reference()
    db = DonneesBeton(
        epaisseur_beton_proprete=0.05,
        formes_dallage=[
            SectionFormeDallage(surface=100.0, epaisseur=0.05),  # pièces de vie
            SectionFormeDallage(surface=54.82, epaisseur=0.08),  # garage, dalle plus épaisse
        ],
    )
    calc = CalculBeton(dt, db)
    attendu = (100.0 * 0.05) + (54.82 * 0.08)
    assert calc.volume_forme_dallage() == pytest.approx(attendu, abs=0.001)


def test_volume_poteaux():
    dt = _donnees_terrassement_reference()
    db = DonneesBeton(
        epaisseur_beton_proprete=0,
        hauteur_poteaux=4.1,
        poteaux=[
            SectionPoteau(section=0.03, nombre=34),
            SectionPoteau(section=0.075, nombre=4),
            SectionPoteau(section=0.08, nombre=2),
            SectionPoteau(section=0.06, nombre=1),
        ],
    )
    calc = CalculBeton(dt, db)
    # (0.03*34+0.075*4+0.08*2+0.06*1) * 4.1 = 1.54 * 4.1
    assert calc.volume_poteaux() == pytest.approx(6.314, abs=0.001)


def test_volume_poteaux_amorces():
    dt = _donnees_terrassement_reference()
    db = DonneesBeton(epaisseur_beton_proprete=0, volume_poteaux_amorces=2.351)
    calc = CalculBeton(dt, db)
    assert calc.volume_poteaux_amorces() == 2.351


def test_volume_poutres():
    dt = _donnees_terrassement_reference()
    db = DonneesBeton(
        epaisseur_beton_proprete=0,
        poutres=[
            SectionPoutre(section=0.06, longueur=11.65),
            SectionPoutre(section=0.10, longueur=5.74),
        ],
    )
    calc = CalculBeton(dt, db)
    assert calc.volume_poutres() == pytest.approx(0.699 + 0.574, abs=0.001)


def test_volume_longrines_vide():
    """Cas limite : aucune longrine définie -> le volume doit être 0, pas une erreur."""
    dt = _donnees_terrassement_reference()
    db = DonneesBeton(epaisseur_beton_proprete=0, longrines=[])
    calc = CalculBeton(dt, db)
    assert calc.volume_longrines() == 0.0


def test_volume_escalier_absent():
    """Cas limite : pas d'escalier défini (None) -> volume 0, pas d'erreur."""
    dt = _donnees_terrassement_reference()
    db = DonneesBeton(epaisseur_beton_proprete=0, escalier=None)
    calc = CalculBeton(dt, db)
    assert calc.volume_escalier() == 0.0


def test_volume_escalier_present():
    dt = _donnees_terrassement_reference()
    db = DonneesBeton(
        epaisseur_beton_proprete=0,
        escalier=DonneesEscalier(
            hauteur_marche=0.17, largeur_marche=0.3, emmarchement=1.0,
            nombre_marches=19, longueur_paillasse=6.5, epaisseur_paillasse=0.12,
            longueur_palier=1.1, largeur_palier=1.0,
        ),
    )
    calc = CalculBeton(dt, db)
    assert calc.volume_escalier() == pytest.approx(1.3965, abs=0.001)


def test_volume_dalle_pleine_placard_cuisine():
    dt = _donnees_terrassement_reference()
    db = DonneesBeton(
        epaisseur_beton_proprete=0,
        epaisseur_dalle_pleine=0.1,
        longueur_placard=2.0, largeur_placard=0.6,
        longueur_paillasse_cuisine=6.2, largeur_paillasse_cuisine=0.6,
    )
    calc = CalculBeton(dt, db)
    assert calc.volume_dalle_pleine_placard_cuisine() == pytest.approx(0.492, abs=0.001)
