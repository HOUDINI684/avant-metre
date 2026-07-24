"""
test_terrassement.py
=====================
Tests unitaires du module terrassement.py.

Chaque test suit le même principe :
1. On construit un objet DonneesTerrassement avec des valeurs connues
2. On calcule une grandeur avec CalculTerrassement
3. On vérifie que le résultat correspond à la valeur attendue

Les valeurs attendues viennent du fichier Excel de référence
(METRE_ARMATURE_modifie_.xlsx), qu'on a vérifiées ensemble à la main.
"""

import pytest
from avant_metre.donnees import DonneesTerrassement, SectionFouille
from avant_metre.terrassement import CalculTerrassement


def test_volume_fouille_rigole():
    """Vérifie le volume de la fouille en rigole seule (sans les trous)."""
    donnees = DonneesTerrassement(
        longueur_developpee_rigole=64.63,
        profondeur_rigole=1.3,
        largeur_rigole=0.5,
    )
    calc = CalculTerrassement(donnees)
    assert calc.volume_fouille_rigole() == pytest.approx(42.0095, abs=0.001)


def test_volume_fouilles_en_trous():
    """Vérifie le volume cumulé de plusieurs types de fouilles en trous."""
    donnees = DonneesTerrassement(
        longueur_developpee_rigole=0,
        profondeur_rigole=0,
        largeur_rigole=0,
        fouilles_en_trous=[
            SectionFouille(surface=2.56, nombre=25),
            SectionFouille(surface=4.0, nombre=2),
            SectionFouille(surface=4.32, nombre=3),
        ],
        profondeur_fouille_trou=1.4,
    )
    calc = CalculTerrassement(donnees)
    # (2.56*25 + 4*2 + 4.32*3) * 1.4 = 84.96 * 1.4 = 118.944
    assert calc.volume_fouilles_en_trous() == pytest.approx(118.944, abs=0.001)


def test_volume_fouilles_total():
    """Vf = rigole + trous. Vérifie la valeur totale du fichier Excel de référence."""
    donnees = DonneesTerrassement(
        longueur_developpee_rigole=64.63,
        profondeur_rigole=1.3,
        largeur_rigole=0.5,
        fouilles_en_trous=[
            SectionFouille(surface=2.56, nombre=25),
            SectionFouille(surface=4.0, nombre=2),
            SectionFouille(surface=4.32, nombre=3),
        ],
        profondeur_fouille_trou=1.4,
    )
    calc = CalculTerrassement(donnees)
    assert calc.volume_fouilles() == pytest.approx(160.9535, abs=0.001)


def test_volume_fouilles_sans_trous():
    """Cas limite : aucune fouille en trous définie -> le terme correspondant vaut 0."""
    donnees = DonneesTerrassement(
        longueur_developpee_rigole=64.63,
        profondeur_rigole=1.3,
        largeur_rigole=0.5,
    )
    calc = CalculTerrassement(donnees)
    assert calc.volume_fouilles_en_trous() == 0.0
    # Vf doit alors être égal au seul terme de la rigole
    assert calc.volume_fouilles() == calc.volume_fouille_rigole()


def test_volume_remblai_apport_locaux():
    donnees = DonneesTerrassement(
        longueur_developpee_rigole=0, profondeur_rigole=0, largeur_rigole=0,
        surface_locaux=154.82, epaisseur_remblai_locaux=0.6,
    )
    calc = CalculTerrassement(donnees)
    assert calc.volume_remblai_apport_locaux() == pytest.approx(92.892, abs=0.001)


def test_volume_remblai_apport_cour():
    donnees = DonneesTerrassement(
        longueur_developpee_rigole=0, profondeur_rigole=0, largeur_rigole=0,
        surface_cour=144.64, epaisseur_remblai_cour=0.4,
    )
    calc = CalculTerrassement(donnees)
    assert calc.volume_remblai_apport_cour() == pytest.approx(57.856, abs=0.001)


def test_volume_mur_sous_bassement_enterre():
    donnees = DonneesTerrassement(
        longueur_developpee_rigole=0, profondeur_rigole=0, largeur_rigole=0,
        longueur_developpee_mur_sous_bassement=135.01,
        hauteur_mur_sous_bassement_enterre=1.0,
        epaisseur_mur_sous_bassement=0.15,
    )
    calc = CalculTerrassement(donnees)
    assert calc.volume_mur_sous_bassement_enterre() == pytest.approx(20.2515, abs=0.001)
