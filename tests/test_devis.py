"""
test_devis.py
==============
Tests unitaires du module devis.py.
"""

import pytest
from avant_metre.donnees import DonneesArmatures
from avant_metre.devis import CalculDevis


def test_quantite_ciment_kg():
    resultats = {"Vbp": 5.864, "Vbf": 30.658}
    devis = CalculDevis(resultats)
    detail = devis.quantite_ciment_kg()
    assert detail["Vbp"] == pytest.approx(5.864 * 150, abs=0.1)
    assert detail["Vbf"] == pytest.approx(30.658 * 300, abs=0.1)


def test_quantite_ciment_sacs_valeurs_reelles():
    """Vérifié contre le vrai fichier Excel de référence."""
    resultats = {"Vbp": 4.545, "Vbf": 15.248}
    devis = CalculDevis(resultats)
    sacs = devis.quantite_ciment_sacs()
    assert sacs["Vbp"] == 14
    assert sacs["Vbf"] == 92


def test_volume_total_beton_et_granulats():
    resultats = {"Vbp": 5.864, "Vbf": 30.658, "Vbfd": 7.741, "Vbst": 23.726, "Vbdp": 0.492, "Vpa": 0}
    devis = CalculDevis(resultats)
    total_attendu = 5.864 + 30.658 + 7.741 + 23.726 + 0.492
    assert devis.volume_total_beton() == pytest.approx(total_attendu, abs=0.01)
    assert devis.quantite_sable_m3() == pytest.approx(total_attendu * 0.4, abs=0.01)
    assert devis.quantite_gravier_m3() == pytest.approx(total_attendu * 0.8, abs=0.01)


def test_quantite_agglos_valeur_reelle():
    """Vérifié contre le vrai fichier Excel de référence (ratio 13/m2)."""
    resultats = {"Smsb": 124.32, "Sme": 0}
    devis = CalculDevis(resultats)
    assert devis.quantite_agglos() == 1617


def test_moulage_et_jointement_agglos_valeurs_reelles():
    resultats = {"Smsb": 124.32, "Sme": 0}
    devis = CalculDevis(resultats)
    assert devis.ciment_moulage_agglos_sacs() == 96
    assert devis.sable_moulage_agglos_m3() == pytest.approx(16.8, abs=0.01)
    assert devis.ciment_jointement_mur_sacs() == 13
    assert devis.sable_jointement_mur_m3() == pytest.approx(1.625, abs=0.01)


def test_nombre_barres_semelles_valeurs_reelles():
    """Vérifié contre le vrai fichier Excel de référence."""
    armatures = DonneesArmatures(
        longueur_ha6_longitudinal_semelle_filante=125.47,
        longueur_ha8_transversal_semelle_filante=124.35,
        longueur_ha10_semelles_isolees=154.36,
    )
    devis = CalculDevis({}, armatures)
    assert devis.nombre_barres_ha6() == 33
    assert devis.nombre_barres_ha8() == 11
    assert devis.nombre_barres_ha10() == 14


def test_armatures_absentes_par_defaut():
    """Cas limite : si on ne fournit pas de DonneesArmatures, tout doit
    valoir 0 plutôt que de planter."""
    devis = CalculDevis({})
    assert devis.nombre_barres_ha6() == 0
    assert devis.nombre_barres_ha8() == 0
    assert devis.nombre_barres_ha10() == 0


def test_poids_acier_structure_kg():
    resultats = {"Vbst": 23.726, "Vbdp": 0.492}
    devis = CalculDevis(resultats)
    detail = devis.poids_acier_structure_kg()
    assert detail["Vbst"] == pytest.approx(23.726 * 120, abs=0.1)
    assert detail["Vbdp"] == pytest.approx(0.492 * 80, abs=0.1)


def test_resultats_incomplets_ne_plantent_pas():
    """Cas limite : si une clé attendue manque dans les résultats (ex: projet
    sans dalle pleine), le devis doit renvoyer 0 pour cette clé, pas planter."""
    resultats = {"Vbp": 5.864}  # Vbf, Vbfd, Vbst, Vbdp, Vpa absents
    devis = CalculDevis(resultats)
    detail = devis.quantite_ciment_kg()
    assert detail["Vbf"] == 0.0
    assert detail["Vbst"] == 0.0

