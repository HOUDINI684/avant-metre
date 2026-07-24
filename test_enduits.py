"""
test_enduits.py
================
Tests unitaires du module enduits.py.
"""

import pytest
from avant_metre.donnees import DonneesEnduits
from avant_metre.enduits import CalculEnduits


def test_surface_mur_elevation_independante():
    de = DonneesEnduits(longueur_mur_elevation=106.85, hauteur_mur_elevation=3.0, surface_baies=40.98)
    calc = CalculEnduits(de)
    assert calc.surface_mur_elevation() == pytest.approx(279.57, abs=0.01)


def test_surface_mur_soubassement_hors_sol_independante():
    de = DonneesEnduits(longueur_mur_soubassement_hors_sol=135.01, hauteur_mur_soubassement_hors_sol=0.3)
    calc = CalculEnduits(de)
    assert calc.surface_mur_soubassement_hors_sol() == pytest.approx(40.503, abs=0.01)


def test_surface_enduit_vertical():
    de = DonneesEnduits(
        longueur_mur_elevation=106.85, hauteur_mur_elevation=3.0, surface_baies=40.98,
        longueur_mur_soubassement_hors_sol=135.01, hauteur_mur_soubassement_hors_sol=0.25,
        surface_acrotere=0.0,
    )
    calc = CalculEnduits(de)
    sm_attendu = 135.01 * 0.25
    attendu = (279.57 * 2) + sm_attendu + 0
    assert calc.surface_enduit_vertical() == pytest.approx(attendu, abs=0.01)


def test_surface_enduit_vertical_avec_acrotere():
    """Vérifie que l'acrotère est bien compté sur ses deux faces (x2),
    comme dans le fichier Excel de référence."""
    de = DonneesEnduits(
        longueur_mur_elevation=50.0, hauteur_mur_elevation=2.0, surface_baies=0.0,
        surface_acrotere=10.0,
    )
    calc = CalculEnduits(de)
    # Sme = 50*2 - 0 = 100 ; EnV = (100*2) + 0 + (10*2) = 200 + 0 + 20 = 220
    assert calc.surface_enduit_vertical() == pytest.approx(220.0, abs=0.01)


def test_surface_enduit_horizontal():
    de = DonneesEnduits(surface_plancher=45.0)
    calc = CalculEnduits(de)
    assert calc.surface_enduit_horizontal() == 45.0


def test_surface_enduit_horizontal_par_defaut():
    """Cas limite : si Sp n'est pas renseigné, EnH doit valoir 0, pas planter."""
    de = DonneesEnduits()
    calc = CalculEnduits(de)
    assert calc.surface_enduit_horizontal() == 0.0
