"""
test_maconnerie.py
===================
Tests unitaires du module maconnerie.py.
"""

import pytest
from avant_metre.donnees import DonneesTerrassement, DonneesAgglos
from avant_metre.maconnerie import CalculMaconnerie


def test_surface_mur_soubassement():
    dt = DonneesTerrassement(
        longueur_developpee_rigole=0, profondeur_rigole=0, largeur_rigole=0,
        longueur_developpee_mur_sous_bassement=135.01,
    )
    da = DonneesAgglos(
        hauteur_mur_soubassement=1.4,
        longueur_developpee_mur_elevation=0,
        hauteur_mur_elevation=0,
    )
    calc = CalculMaconnerie(dt, da)
    assert calc.surface_mur_soubassement() == pytest.approx(189.014, abs=0.01)


def test_surface_mur_elevation():
    dt = DonneesTerrassement(longueur_developpee_rigole=0, profondeur_rigole=0, largeur_rigole=0)
    da = DonneesAgglos(
        hauteur_mur_soubassement=0,
        longueur_developpee_mur_elevation=106.85,
        hauteur_mur_elevation=3.0,
        surface_baies=40.98,
    )
    calc = CalculMaconnerie(dt, da)
    # (106.85 * 3) - 40.98
    assert calc.surface_mur_elevation() == pytest.approx(279.57, abs=0.01)


def test_surface_mur_elevation_sans_baies():
    """Cas limite : aucune baie renseignée -> rien à déduire."""
    dt = DonneesTerrassement(longueur_developpee_rigole=0, profondeur_rigole=0, largeur_rigole=0)
    da = DonneesAgglos(
        hauteur_mur_soubassement=0,
        longueur_developpee_mur_elevation=50.0,
        hauteur_mur_elevation=3.0,
    )
    calc = CalculMaconnerie(dt, da)
    assert calc.surface_mur_elevation() == pytest.approx(150.0, abs=0.01)
