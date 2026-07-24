"""
main.py
=======
Exemple d'utilisation complète du package avant_metre, avec les données
issues du fichier Excel de référence (METRE_ARMATURE_modifie_.xlsx).

Certaines valeurs sont des hypothèses à confirmer (voir commentaires) :
- largeur_semelle_filante_beton (lbp) : 0.40 m
- longueur_developpee_chainage : 106.85 m (= ldme)
- formule de Sme : ldme x Htme - Sb (sans additionner ldms)
"""

from avant_metre.donnees import (
    DonneesTerrassement, SectionFouille,
    DonneesBeton, SectionPoteau, SectionPoutre, DonneesEscalier,
    SectionSemelleFilante, SectionSemelleIsolee, SectionFormeDallage,
    DonneesAgglos, DonneesEnduits, DonneesArmatures, DonneesArmaturesDetaillees,
)
from avant_metre.projet import AvantMetreProjet
from avant_metre.devis import CalculDevis
from avant_metre.armature import CalculArmature


def construire_projet_exemple() -> AvantMetreProjet:
    donnees_terrassement = DonneesTerrassement(
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
        surface_cour=144.64,
        epaisseur_remblai_locaux=0.6,
        epaisseur_remblai_cour=0.4,
        hauteur_mur_sous_bassement_enterre=1.0,
        epaisseur_mur_sous_bassement=0.15,
        longueur_developpee_mur_sous_bassement=135.01,
    )

    donnees_beton = DonneesBeton(
        epaisseur_beton_proprete=0.05,
        semelles_filantes=[
            SectionSemelleFilante(longueur=64.63, largeur=0.40, epaisseur=0.2),
        ],
        semelles_isolees=[
            SectionSemelleIsolee(surface=2.56, nombre=25, epaisseur=0.3),
            SectionSemelleIsolee(surface=4.0, nombre=2, epaisseur=0.3),
            SectionSemelleIsolee(surface=4.32, nombre=3, epaisseur=0.3),
        ],
        formes_dallage=[
            SectionFormeDallage(surface=154.82, epaisseur=0.05),
        ],
        hauteur_poteaux=4.1,
        poteaux=[
            SectionPoteau(section=0.03, nombre=34),
            SectionPoteau(section=0.075, nombre=4),
            SectionPoteau(section=0.08, nombre=2),
            SectionPoteau(section=0.06, nombre=1),
        ],
        poutres=[
            SectionPoutre(section=0.06, longueur=11.65),
            SectionPoutre(section=0.06, longueur=23.3),
            SectionPoutre(section=0.06, longueur=16.7),
            SectionPoutre(section=0.06, longueur=11.48),
            SectionPoutre(section=0.10, longueur=5.74),
            SectionPoutre(section=0.12, longueur=6.25),
            SectionPoutre(section=0.06, longueur=9.5),
            SectionPoutre(section=0.06, longueur=4.55),
            SectionPoutre(section=0.03, longueur=121.67),
        ],
        longrines=[],
        section_chainage=0.06,
        longueur_developpee_chainage=106.85,  # HYPOTHESE a confirmer
        escalier=DonneesEscalier(
            hauteur_marche=0.17,
            largeur_marche=0.3,
            emmarchement=1.0,
            nombre_marches=19,
            longueur_paillasse=6.5,
            epaisseur_paillasse=0.12,
            longueur_palier=1.1,
            largeur_palier=1.0,
        ),
        epaisseur_dalle_pleine=0.1,
        longueur_placard=2.0,
        largeur_placard=0.6,
        longueur_paillasse_cuisine=6.2,
        largeur_paillasse_cuisine=0.6,
        volume_poteaux_amorces=2.351,
    )

    donnees_agglos = DonneesAgglos(
        hauteur_mur_soubassement=1.4,
        longueur_developpee_mur_elevation=106.85,
        hauteur_mur_elevation=3.0,
        surface_baies=40.98,
    )

    donnees_enduits = DonneesEnduits(
        longueur_mur_elevation=106.85,
        hauteur_mur_elevation=3.0,
        surface_baies=40.98,
        longueur_mur_soubassement_hors_sol=135.01,
        hauteur_mur_soubassement_hors_sol=0.25,
        surface_acrotere=0.0,
        surface_plancher=0.0,  # non renseigne dans le fichier source
    )

    return AvantMetreProjet(
        nom_projet="Villa - fichier de reference",
        donnees_terrassement=donnees_terrassement,
        donnees_beton=donnees_beton,
        donnees_agglos=donnees_agglos,
        donnees_enduits=donnees_enduits,
    )


def construire_armatures_exemple() -> DonneesArmatures:
    return DonneesArmatures(
        longueur_ha6_longitudinal_semelle_filante=125.47,
        longueur_ha8_transversal_semelle_filante=124.35,
        longueur_ha10_semelles_isolees=154.36,
    )


if __name__ == "__main__":
    projet = construire_projet_exemple()
    print(projet.tableau())

    print()
    devis = CalculDevis(projet.resume_complet(), construire_armatures_exemple())
    print(devis.tableau())

    print()
    print("=" * 60)
    print("CALCUL DETAILLE DE L'ARMATURE — TOUT LE GROS OEUVRE")
    print("(valeurs par defaut : a calibrer avec l'architecte / BE structure)")
    print("=" * 60)
    calcul_armature = CalculArmature(projet.beton.db, DonneesArmaturesDetaillees())
    for element, valeurs in calcul_armature.resume().items():
        print(f"\n{element} :")
        if isinstance(valeurs, dict):
            for cle, val in valeurs.items():
                print(f"  {cle} : {val}")
