"""
app.py
======
Interface web (Streamlit) pour l'avant-métré.

Cette interface réutilise directement le package avant_metre/ qu'on a
construit et testé - aucune formule n'est réécrite ici, on se contente
d'afficher des champs de saisie et de brancher les résultats.

Pour lancer l'application :
    streamlit run app.py
"""

import streamlit as st
import pandas as pd

from avant_metre.donnees import (
    DonneesTerrassement, SectionFouille,
    DonneesBeton, SectionPoteau, SectionPoutre, SectionLongrine, DonneesEscalier,
    SectionSemelleFilante, SectionSemelleIsolee, SectionFormeDallage,
    DonneesAgglos, DonneesEnduits, DonneesArmatures,
    DonneesArmaturesDetaillees, FerraillageLineaire,
    FerraillageSemelleFilante, FerraillageSemelleIsolee, FerraillageDallePleine,
)
from avant_metre.maconnerie import CalculMaconnerie
from avant_metre.projet import AvantMetreProjet
from avant_metre.devis import CalculDevis
from avant_metre.armature import CalculArmature


st.set_page_config(page_title="Avant-métré automatique", page_icon="🏗️", layout="centered")
st.title("🏗️ Avant-métré automatique")

with st.sidebar:
    nom_projet = st.text_input("Nom du projet", value="Mon projet")
    st.caption("Ce nom apparaîtra dans le résumé et les exports.")

(onglet_terrassement, onglet_beton, onglet_maconnerie, onglet_enduits, onglet_armatures,
 onglet_armature_detaillee, onglet_resultats, onglet_devis) = st.tabs(
    ["Terrassement", "Béton", "Maçonnerie", "Enduits", "Armatures",
     "Armature détaillée", "Résultats", "Devis"]
)

# ----------------------------------------------------------------------
# ONGLET : TERRASSEMENT
# ----------------------------------------------------------------------

with onglet_terrassement:
    st.subheader("Fouille en rigole (semelle filante)")
    col1, col2, col3 = st.columns(3)
    with col1:
        ldfr = st.number_input("Longueur développée (m)", value=64.63, min_value=0.0, step=0.1)
    with col2:
        ht = st.number_input("Profondeur (m)", value=1.3, min_value=0.0, step=0.1)
    with col3:
        l = st.number_input("Largeur (m)", value=0.5, min_value=0.0, step=0.05)

    st.subheader("Fouilles en trous (semelles isolées)")
    st.caption("Ajoute ou supprime des lignes selon les types de fouilles de ton projet.")
    df_fouilles = st.data_editor(
        pd.DataFrame({"Surface (m²)": [2.56, 4.32], "Nombre": [25, 3]}),
        num_rows="dynamic", key="editeur_fouilles", use_container_width=True,
    )
    fouilles_en_trous = [
        SectionFouille(surface=float(row["Surface (m²)"]), nombre=int(row["Nombre"]))
        for _, row in df_fouilles.iterrows()
        if row["Surface (m²)"] and row["Surface (m²)"] > 0 and row["Nombre"] and row["Nombre"] > 0
    ]
    htt = st.number_input("Profondeur des fouilles en trous (m)", value=1.4, min_value=0.0, step=0.1)

    st.subheader("Remblais")
    col1, col2 = st.columns(2)
    with col1:
        surface_locaux = st.number_input("Surface des locaux (m²)", value=154.82, min_value=0.0, step=1.0)
        epaisseur_remblai_locaux = st.number_input("Épaisseur remblai locaux (m)", value=0.6, min_value=0.0, step=0.05)
    with col2:
        surface_cour = st.number_input("Surface de la cour (m²)", value=144.64, min_value=0.0, step=1.0)
        epaisseur_remblai_cour = st.number_input("Épaisseur remblai cour (m)", value=0.4, min_value=0.0, step=0.05)

    st.subheader("Mur de soubassement enterré")
    st.caption("Utile pour le calcul du remblai et pour la maçonnerie (onglet suivant).")
    col1, col2, col3 = st.columns(3)
    with col1:
        ldms = st.number_input("Longueur développée (m)", value=135.01, min_value=0.0, step=0.1, key="ldms")
    with col2:
        htmse = st.number_input("Hauteur enterrée (m)", value=1.0, min_value=0.0, step=0.1)
    with col3:
        epm = st.number_input("Épaisseur du mur (m)", value=0.15, min_value=0.0, step=0.01)

donnees_terrassement = DonneesTerrassement(
    longueur_developpee_rigole=ldfr, profondeur_rigole=ht, largeur_rigole=l,
    fouilles_en_trous=fouilles_en_trous, profondeur_fouille_trou=htt,
    surface_locaux=surface_locaux, surface_cour=surface_cour,
    epaisseur_remblai_locaux=epaisseur_remblai_locaux, epaisseur_remblai_cour=epaisseur_remblai_cour,
    hauteur_mur_sous_bassement_enterre=htmse, epaisseur_mur_sous_bassement=epm,
    longueur_developpee_mur_sous_bassement=ldms,
)

# ----------------------------------------------------------------------
# ONGLET : BETON
# ----------------------------------------------------------------------

with onglet_beton:
    st.subheader("Béton de propreté")
    epbp = st.number_input("Épaisseur béton propreté (m)", value=0.05, min_value=0.0, step=0.01,
                            help="Suit la même emprise que les fouilles, une seule épaisseur.")

    st.subheader("Semelles filantes")
    st.caption("Ajoute autant de types que nécessaire (longueur x largeur x épaisseur).")
    df_semelles_filantes = st.data_editor(
        pd.DataFrame({"Longueur (m)": [64.63], "Largeur (m)": [0.40], "Épaisseur (m)": [0.2]}),
        num_rows="dynamic", key="editeur_semelles_filantes", use_container_width=True,
    )
    semelles_filantes = [
        SectionSemelleFilante(
            longueur=float(row["Longueur (m)"]), largeur=float(row["Largeur (m)"]),
            epaisseur=float(row["Épaisseur (m)"]),
        )
        for _, row in df_semelles_filantes.iterrows()
        if row["Longueur (m)"] and row["Longueur (m)"] > 0
    ]

    st.subheader("Semelles isolées")
    st.caption("Ajoute autant de types que nécessaire (surface x nombre x épaisseur).")
    df_semelles_isolees = st.data_editor(
        pd.DataFrame({"Surface (m²)": [2.56, 4.0, 4.32], "Nombre": [25, 2, 3], "Épaisseur (m)": [0.3, 0.3, 0.3]}),
        num_rows="dynamic", key="editeur_semelles_isolees", use_container_width=True,
    )
    semelles_isolees = [
        SectionSemelleIsolee(
            surface=float(row["Surface (m²)"]), nombre=int(row["Nombre"]),
            epaisseur=float(row["Épaisseur (m)"]),
        )
        for _, row in df_semelles_isolees.iterrows()
        if row["Surface (m²)"] and row["Surface (m²)"] > 0 and row["Nombre"] and row["Nombre"] > 0
    ]

    st.subheader("Forme de dallage")
    st.caption("Ajoute plusieurs zones si l'épaisseur diffère selon les pièces (ex: garage vs pièces de vie).")
    df_formes_dallage = st.data_editor(
        pd.DataFrame({"Surface (m²)": [154.82], "Épaisseur (m)": [0.05]}),
        num_rows="dynamic", key="editeur_formes_dallage", use_container_width=True,
    )
    formes_dallage = [
        SectionFormeDallage(surface=float(row["Surface (m²)"]), epaisseur=float(row["Épaisseur (m)"]))
        for _, row in df_formes_dallage.iterrows()
        if row["Surface (m²)"] and row["Surface (m²)"] > 0
    ]

    st.subheader("Poteaux amorces")
    st.caption("Tronçons de poteaux émergeant des semelles, avant les poteaux en élévation.")
    volume_poteaux_amorces = st.number_input("Volume poteaux amorces (m³)", value=2.351, min_value=0.0, step=0.1)

    st.subheader("Poteaux")
    hauteur_poteaux = st.number_input("Hauteur des poteaux (m)", value=4.1, min_value=0.0, step=0.1)
    df_poteaux = st.data_editor(
        pd.DataFrame({"Section (m²)": [0.03, 0.075, 0.08], "Nombre": [34, 4, 2]}),
        num_rows="dynamic", key="editeur_poteaux", use_container_width=True,
    )
    poteaux = [
        SectionPoteau(section=float(row["Section (m²)"]), nombre=int(row["Nombre"]))
        for _, row in df_poteaux.iterrows()
        if row["Section (m²)"] and row["Section (m²)"] > 0 and row["Nombre"] and row["Nombre"] > 0
    ]

    st.subheader("Poutres")
    df_poutres = st.data_editor(
        pd.DataFrame({"Section (m²)": [0.06, 0.10, 0.12], "Longueur développée (m)": [11.65, 5.74, 6.25]}),
        num_rows="dynamic", key="editeur_poutres", use_container_width=True,
    )
    poutres = [
        SectionPoutre(section=float(row["Section (m²)"]), longueur=float(row["Longueur développée (m)"]))
        for _, row in df_poutres.iterrows()
        if row["Section (m²)"] and row["Section (m²)"] > 0 and row["Longueur développée (m)"] and row["Longueur développée (m)"] > 0
    ]

    st.subheader("Longrines")
    st.caption("Laisse le tableau vide s'il n'y en a pas.")
    df_longrines = st.data_editor(
        pd.DataFrame({"Section (m²)": [], "Longueur développée (m)": []}),
        num_rows="dynamic", key="editeur_longrines", use_container_width=True,
    )
    longrines = [
        SectionLongrine(section=float(row["Section (m²)"]), longueur=float(row["Longueur développée (m)"]))
        for _, row in df_longrines.iterrows()
        if row["Section (m²)"] and row["Section (m²)"] > 0 and row["Longueur développée (m)"] and row["Longueur développée (m)"] > 0
    ]

    st.subheader("Chaînages")
    col1, col2 = st.columns(2)
    with col1:
        section_chainage = st.number_input("Section combinée bas+haut (m²)", value=0.06, min_value=0.0, step=0.01)
    with col2:
        longueur_chainage = st.number_input("Longueur développée (m)", value=106.85, min_value=0.0, step=0.1)

    st.subheader("Escalier")
    a_un_escalier = st.checkbox("Le projet a un escalier en béton", value=True)
    escalier = None
    if a_un_escalier:
        col1, col2, col3 = st.columns(3)
        with col1:
            htm = st.number_input("Hauteur de marche (m)", value=0.17, min_value=0.0, step=0.01)
        with col2:
            lm = st.number_input("Largeur de marche (m)", value=0.3, min_value=0.0, step=0.01)
        with col3:
            emmarchement = st.number_input("Emmarchement (m)", value=1.0, min_value=0.0, step=0.1)
        col1, col2, col3 = st.columns(3)
        with col1:
            nm = st.number_input("Nombre de marches", value=19, min_value=0, step=1)
        with col2:
            lp_esc = st.number_input("Longueur paillasse (m)", value=6.5, min_value=0.0, step=0.1)
        with col3:
            epp = st.number_input("Épaisseur paillasse (m)", value=0.12, min_value=0.0, step=0.01)
        col1, col2 = st.columns(2)
        with col1:
            lpr = st.number_input("Longueur palier (m)", value=1.1, min_value=0.0, step=0.1)
        with col2:
            lpr_l = st.number_input("Largeur palier (m)", value=1.0, min_value=0.0, step=0.1)
        escalier = DonneesEscalier(
            hauteur_marche=htm, largeur_marche=lm, emmarchement=emmarchement,
            nombre_marches=nm, longueur_paillasse=lp_esc, epaisseur_paillasse=epp,
            longueur_palier=lpr, largeur_palier=lpr_l,
        )

    st.subheader("Dalle pleine (placard / paillasse cuisine)")
    col1, col2, col3 = st.columns(3)
    with col1:
        eppc = st.number_input("Épaisseur dalle pleine (m)", value=0.1, min_value=0.0, step=0.01)
    with col2:
        lp_placard = st.number_input("Longueur placard (m)", value=2.0, min_value=0.0, step=0.1)
        lp_placard_l = st.number_input("Largeur placard (m)", value=0.6, min_value=0.0, step=0.1)
    with col3:
        lpc_cuisine = st.number_input("Longueur paillasse cuisine (m)", value=6.2, min_value=0.0, step=0.1)
        lpc_cuisine_l = st.number_input("Largeur paillasse cuisine (m)", value=0.6, min_value=0.0, step=0.1)

donnees_beton = DonneesBeton(
    epaisseur_beton_proprete=epbp,
    semelles_filantes=semelles_filantes,
    semelles_isolees=semelles_isolees,
    formes_dallage=formes_dallage,
    hauteur_poteaux=hauteur_poteaux,
    poteaux=poteaux, poutres=poutres, longrines=longrines,
    section_chainage=section_chainage, longueur_developpee_chainage=longueur_chainage,
    escalier=escalier, epaisseur_dalle_pleine=eppc,
    longueur_placard=lp_placard, largeur_placard=lp_placard_l,
    longueur_paillasse_cuisine=lpc_cuisine, largeur_paillasse_cuisine=lpc_cuisine_l,
    volume_poteaux_amorces=volume_poteaux_amorces,
)

# ----------------------------------------------------------------------
# ONGLET : MACONNERIE
# ----------------------------------------------------------------------

with onglet_maconnerie:
    st.subheader("Murs en agglos")
    col1, col2, col3 = st.columns(3)
    with col1:
        htms = st.number_input("Hauteur mur soubassement (m)", value=1.4, min_value=0.0, step=0.1)
    with col2:
        ldme = st.number_input("Longueur développée mur élévation (m)", value=106.85, min_value=0.0, step=0.1)
    with col3:
        htme = st.number_input("Hauteur mur élévation (m)", value=3.0, min_value=0.0, step=0.1)
    sb = st.number_input("Surface des baies à déduire (m²)", value=40.98, min_value=0.0, step=1.0,
                          help="Portes et fenêtres : leur surface ne compte pas dans le mur en agglos.")

donnees_agglos = DonneesAgglos(
    hauteur_mur_soubassement=htms, longueur_developpee_mur_elevation=ldme,
    hauteur_mur_elevation=htme, surface_baies=sb,
)
# Calcul immédiat de la maçonnerie (avant l'onglet Enduits, qui en affiche
# une valeur de référence en lecture seule).
calcul_maconnerie = CalculMaconnerie(donnees_terrassement, donnees_agglos)
smsb_reference = calcul_maconnerie.surface_mur_soubassement()
sme_reference = calcul_maconnerie.surface_mur_elevation()

# ----------------------------------------------------------------------
# ONGLET : ENDUITS
# ----------------------------------------------------------------------

with onglet_enduits:
    st.subheader("Enduit vertical")

    st.markdown("**Valeurs de référence (calculées dans l'onglet Maçonnerie)**")
    c1, c2 = st.columns(2)
    c1.metric("Sme (Maçonnerie)", f"{sme_reference:.2f} m²")
    c2.metric("Smsb (Maçonnerie)", f"{smsb_reference:.2f} m²")
    st.caption("Ces valeurs sont affichées pour référence uniquement. Le calcul de l'enduit "
               "vertical ci-dessous utilise ses propres dimensions, saisies indépendamment.")

    st.markdown("**Calcul indépendant pour l'enduit**")
    st.caption("Surface de mur en élévation (Sme)")
    col1, col2, col3 = st.columns(3)
    with col1:
        ldme_enduit = st.number_input("Longueur développée (m)", value=106.85, min_value=0.0, step=0.1, key="ldme_enduit")
    with col2:
        htme_enduit = st.number_input("Hauteur (m)", value=3.0, min_value=0.0, step=0.1, key="htme_enduit")
    with col3:
        sb_enduit = st.number_input("Surface des baies (m²)", value=40.98, min_value=0.0, step=1.0, key="sb_enduit")

    st.caption("Portion de mur de soubassement hors terrain naturel (Sm)")
    col1, col2 = st.columns(2)
    with col1:
        ldms_enduit = st.number_input("Longueur développée (m)", value=135.01, min_value=0.0, step=0.1, key="ldms_enduit")
    with col2:
        htms_hors_sol = st.number_input("Hauteur hors-sol (m)", value=0.25, min_value=0.0, step=0.01, key="htms_hors_sol")

    sa = st.number_input("Surface acrotère (m²)", value=0.0, min_value=0.0, step=1.0)

    st.subheader("Enduit horizontal")
    sp = st.number_input("Surface plancher (m²)", value=0.0, min_value=0.0, step=1.0)

donnees_enduits = DonneesEnduits(
    longueur_mur_elevation=ldme_enduit, hauteur_mur_elevation=htme_enduit, surface_baies=sb_enduit,
    longueur_mur_soubassement_hors_sol=ldms_enduit, hauteur_mur_soubassement_hors_sol=htms_hors_sol,
    surface_acrotere=sa, surface_plancher=sp,
)

# ----------------------------------------------------------------------
# ONGLET : ARMATURES
# ----------------------------------------------------------------------

with onglet_armatures:
    st.subheader("Armatures des semelles")
    st.caption("Longueurs développées totales, utilisées pour calculer le nombre de barres "
               "commerciales (11,6 m) à commander, par diamètre.")
    ld_ha6 = st.number_input("Longueur HA6 - longitudinal semelle filante (m)", value=125.47, min_value=0.0, step=1.0)
    ld_ha8 = st.number_input("Longueur HA8 - transversal semelle filante (m)", value=124.35, min_value=0.0, step=1.0)
    ld_ha10 = st.number_input("Longueur HA10 - semelles isolées (m)", value=154.36, min_value=0.0, step=1.0)

donnees_armatures = DonneesArmatures(
    longueur_ha6_longitudinal_semelle_filante=ld_ha6,
    longueur_ha8_transversal_semelle_filante=ld_ha8,
    longueur_ha10_semelles_isolees=ld_ha10,
)

# ----------------------------------------------------------------------
# CALCUL GLOBAL
# ----------------------------------------------------------------------

projet = AvantMetreProjet(
    nom_projet=nom_projet,
    donnees_terrassement=donnees_terrassement,
    donnees_beton=donnees_beton,
    donnees_agglos=donnees_agglos,
    donnees_enduits=donnees_enduits,
)
resultats = projet.resume_complet()
devis = CalculDevis(resultats, donnees_armatures)

# ----------------------------------------------------------------------
# ONGLET : ARMATURE DETAILLEE (tout le gros œuvre)
# ----------------------------------------------------------------------

with onglet_armature_detaillee:
    st.subheader("Calcul détaillé de l'armature — tout le gros œuvre")
    st.caption(
        "Contrairement à l'onglet « Armatures » (qui prend des longueurs déjà "
        "calculées), cet onglet calcule lui-même les longueurs de fer à partir "
        "de l'espacement, du nombre de barres et de l'enrobage — pour les "
        "semelles, poteaux, poutres, longrines, chaînages et la dalle pleine. "
        "L'escalier reste estimé par un ratio de treillis soudé (sa géométrie "
        "en pente ne se prête pas à un calcul simple sans plan dédié)."
    )
    st.info(
        "Les valeurs par défaut ci-dessous sont des pratiques courantes de la "
        "profession, **à faire valider par l'architecte ou le bureau d'études "
        "structure** avant de les considérer comme définitives pour ce projet.",
        icon="⚠️",
    )

    col1, col2, col3 = st.columns(3)
    enrobage_fondation = col1.number_input("Enrobage fondations (cm)", value=5.0, min_value=0.0, step=0.5)
    enrobage_elevation = col2.number_input("Enrobage élévation (cm)", value=2.5, min_value=0.0, step=0.5)
    coef_recouvrement = col3.number_input("Coefficient de recouvrement (x diamètre)", value=50.0, min_value=0.0, step=5.0)

    with st.expander("Semelle filante", expanded=False):
        c1, c2 = st.columns(2)
        sf_nb_long = c1.number_input("Nombre de barres longitudinales", value=3, min_value=0, step=1, key="sf_nb")
        sf_diam_long = c2.number_input("Diamètre longitudinal (mm)", value=6, min_value=0, step=1, key="sf_dl")
        c1, c2 = st.columns(2)
        sf_diam_rep = c1.number_input("Diamètre répartition (mm)", value=8, min_value=0, step=1, key="sf_dr")
        sf_esp_rep = c2.number_input("Espacement répartition (cm)", value=25.0, min_value=1.0, step=1.0, key="sf_er")

    with st.expander("Semelle isolée", expanded=False):
        c1, c2 = st.columns(2)
        si_diam = c1.number_input("Diamètre (mm)", value=10, min_value=0, step=1, key="si_d")
        si_esp = c2.number_input("Espacement (cm)", value=15.0, min_value=1.0, step=1.0, key="si_e")
        st.caption("Astuce : renseigne cote_x/cote_y sur chaque semelle isolée (onglet Béton) "
                   "pour un calcul précis. Sans ça, une forme carrée est déduite de la surface.")

    with st.expander("Poteaux", expanded=False):
        c1, c2 = st.columns(2)
        po_nb_long = c1.number_input("Nombre de barres longitudinales", value=4, min_value=0, step=1, key="po_nb")
        po_diam_long = c2.number_input("Diamètre longitudinal (mm)", value=12, min_value=0, step=1, key="po_dl")
        c1, c2 = st.columns(2)
        po_diam_cadre = c1.number_input("Diamètre cadres (mm)", value=6, min_value=0, step=1, key="po_dc")
        po_esp_cadre = c2.number_input("Espacement cadres (cm)", value=15.0, min_value=1.0, step=1.0, key="po_ec")

    with st.expander("Poutres", expanded=False):
        c1, c2 = st.columns(2)
        pp_nb_long = c1.number_input("Nombre de barres longitudinales", value=4, min_value=0, step=1, key="pp_nb")
        pp_diam_long = c2.number_input("Diamètre longitudinal (mm)", value=12, min_value=0, step=1, key="pp_dl")
        c1, c2 = st.columns(2)
        pp_diam_cadre = c1.number_input("Diamètre cadres (mm)", value=6, min_value=0, step=1, key="pp_dc")
        pp_esp_cadre = c2.number_input("Espacement cadres (cm)", value=20.0, min_value=1.0, step=1.0, key="pp_ec")
        st.caption("Astuce : renseigne largeur/hauteur sur chaque poutre (onglet Béton) "
                   "pour un calcul précis des cadres. Sans ça, une section carrée est déduite.")

    with st.expander("Longrines", expanded=False):
        c1, c2 = st.columns(2)
        lg_nb_long = c1.number_input("Nombre de barres longitudinales", value=4, min_value=0, step=1, key="lg_nb")
        lg_diam_long = c2.number_input("Diamètre longitudinal (mm)", value=10, min_value=0, step=1, key="lg_dl")
        c1, c2 = st.columns(2)
        lg_diam_cadre = c1.number_input("Diamètre cadres (mm)", value=6, min_value=0, step=1, key="lg_dc")
        lg_esp_cadre = c2.number_input("Espacement cadres (cm)", value=20.0, min_value=1.0, step=1.0, key="lg_ec")

    with st.expander("Chaînages", expanded=False):
        c1, c2 = st.columns(2)
        ch_nb_long = c1.number_input("Nombre de barres longitudinales", value=4, min_value=0, step=1, key="ch_nb")
        ch_diam_long = c2.number_input("Diamètre longitudinal (mm)", value=10, min_value=0, step=1, key="ch_dl")
        c1, c2 = st.columns(2)
        ch_diam_cadre = c1.number_input("Diamètre cadres (mm)", value=6, min_value=0, step=1, key="ch_dc")
        ch_esp_cadre = c2.number_input("Espacement cadres (cm)", value=20.0, min_value=1.0, step=1.0, key="ch_ec")
        c1, c2 = st.columns(2)
        ch_cote_a = c1.number_input("Côté a de la section (m)", value=0.15, min_value=0.0, step=0.01, key="ch_ca")
        ch_cote_b = c2.number_input("Côté b de la section (m)", value=0.15, min_value=0.0, step=0.01, key="ch_cb")

    with st.expander("Dalle pleine", expanded=False):
        c1, c2 = st.columns(2)
        dp_diam = c1.number_input("Diamètre (mm)", value=6, min_value=0, step=1, key="dp_d")
        dp_esp = c2.number_input("Espacement (cm)", value=20.0, min_value=1.0, step=1.0, key="dp_e")

    with st.expander("Escalier (estimation)", expanded=False):
        esc_ratio = st.number_input("Ratio treillis soudé (kg/m²)", value=3.0, min_value=0.0, step=0.5, key="esc_r")

    donnees_armatures_detaillees = DonneesArmaturesDetaillees(
        enrobage_fondation_cm=enrobage_fondation,
        enrobage_elevation_cm=enrobage_elevation,
        coefficient_recouvrement_diametre=coef_recouvrement,
        semelle_filante=FerraillageSemelleFilante(
            nb_barres_longitudinales=sf_nb_long, diametre_longitudinal_mm=sf_diam_long,
            diametre_repartition_mm=sf_diam_rep, espacement_repartition_cm=sf_esp_rep),
        semelle_isolee=FerraillageSemelleIsolee(diametre_mm=si_diam, espacement_cm=si_esp),
        poteaux=FerraillageLineaire(
            nb_barres_longitudinales=po_nb_long, diametre_longitudinal_mm=po_diam_long,
            diametre_cadre_mm=po_diam_cadre, espacement_cadre_cm=po_esp_cadre),
        poutres=FerraillageLineaire(
            nb_barres_longitudinales=pp_nb_long, diametre_longitudinal_mm=pp_diam_long,
            diametre_cadre_mm=pp_diam_cadre, espacement_cadre_cm=pp_esp_cadre),
        longrines=FerraillageLineaire(
            nb_barres_longitudinales=lg_nb_long, diametre_longitudinal_mm=lg_diam_long,
            diametre_cadre_mm=lg_diam_cadre, espacement_cadre_cm=lg_esp_cadre),
        chainages=FerraillageLineaire(
            nb_barres_longitudinales=ch_nb_long, diametre_longitudinal_mm=ch_diam_long,
            diametre_cadre_mm=ch_diam_cadre, espacement_cadre_cm=ch_esp_cadre,
            cote_a=ch_cote_a, cote_b=ch_cote_b),
        dalle_pleine=FerraillageDallePleine(diametre_mm=dp_diam, espacement_cm=dp_esp),
        ratio_treillis_escalier_kg_m2=esc_ratio,
    )

    calcul_armature = CalculArmature(donnees_beton, donnees_armatures_detaillees)
    resume_armature = calcul_armature.resume()

    st.markdown("---")
    st.markdown("**Longueurs de fer par élément**")
    df_elements = pd.DataFrame([
        {"Élément": "Semelle filante — longitudinal", "Longueur (m)": resume_armature["semelle_filante"]["longitudinal_m"]},
        {"Élément": "Semelle filante — répartition", "Longueur (m)": resume_armature["semelle_filante"]["repartition_m"]},
        {"Élément": "Semelle isolée — quadrillage", "Longueur (m)": resume_armature["semelle_isolee"]["quadrillage_m"]},
        {"Élément": "Poteaux — longitudinal", "Longueur (m)": resume_armature["poteaux"]["longitudinal_m"]},
        {"Élément": "Poteaux — cadres", "Longueur (m)": resume_armature["poteaux"]["cadres_m"]},
        {"Élément": "Poutres — longitudinal", "Longueur (m)": resume_armature["poutres"]["longitudinal_m"]},
        {"Élément": "Poutres — cadres", "Longueur (m)": resume_armature["poutres"]["cadres_m"]},
        {"Élément": "Longrines — longitudinal", "Longueur (m)": resume_armature["longrines"]["longitudinal_m"]},
        {"Élément": "Longrines — cadres", "Longueur (m)": resume_armature["longrines"]["cadres_m"]},
        {"Élément": "Chaînages — longitudinal", "Longueur (m)": resume_armature["chainages"]["longitudinal_m"]},
        {"Élément": "Chaînages — cadres", "Longueur (m)": resume_armature["chainages"]["cadres_m"]},
        {"Élément": "Dalle pleine — quadrillage", "Longueur (m)": resume_armature["dalle_pleine"]["quadrillage_m"]},
    ])
    st.dataframe(df_elements, hide_index=True, use_container_width=True)

    st.markdown("**Commande groupée par diamètre (barres de 11,6 m)**")
    barres = resume_armature["barres_par_diametre"]
    if barres:
        df_barres = pd.DataFrame([
            {"Diamètre": f"HA{diam}", "Longueur totale (m)": v["longueur_totale_m"],
             "Barres à commander": v["nb_barres_commerciales"]}
            for diam, v in barres.items()
        ])
        st.dataframe(df_barres, hide_index=True, use_container_width=True)
    else:
        st.caption("Aucune donnée géométrique saisie pour l'instant (onglet Béton).")

    st.markdown("**Escalier (estimation, hors calcul détaillé)**")
    c1, c2 = st.columns(2)
    c1.metric("Surface paillasse", f"{resume_armature['escalier_estimation']['surface_paillasse_m2']:.2f} m²")
    c2.metric("Poids treillis soudé", f"{resume_armature['escalier_estimation']['poids_treillis_kg']:.1f} kg")

# ----------------------------------------------------------------------
# ONGLET : RESULTATS
# ----------------------------------------------------------------------

with onglet_resultats:
    st.subheader(f"Avant-métré — {nom_projet}")

    st.markdown("**Terrassement**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Vf", f"{resultats['Vf']:.2f} m³")
    c2.metric("Vrpf", f"{resultats['Vrpf']:.2f} m³")
    c3.metric("Vrtal", f"{resultats['Vrtal']:.2f} m³")
    c4.metric("Vrtac", f"{resultats['Vrtac']:.2f} m³")

    st.markdown("**Béton**")
    c1, c2, c3 = st.columns(3)
    c1.metric("Vbp", f"{resultats['Vbp']:.2f} m³")
    c2.metric("Vbf", f"{resultats['Vbf']:.2f} m³")
    c3.metric("Vbfd", f"{resultats['Vbfd']:.2f} m³")
    c1, c2 = st.columns(2)
    c1.metric("Vpa", f"{resultats['Vpa']:.2f} m³")
    c2.metric("Vbst", f"{resultats['Vbst']:.2f} m³")
    st.metric("Vbdp", f"{resultats['Vbdp']:.2f} m³")

    st.markdown("**Maçonnerie**")
    c1, c2 = st.columns(2)
    c1.metric("Smsb", f"{resultats['Smsb']:.2f} m²")
    c2.metric("Sme", f"{resultats['Sme']:.2f} m²")

    st.markdown("**Enduits**")
    c1, c2 = st.columns(2)
    c1.metric("EnV", f"{resultats['EnV']:.2f} m²")
    c2.metric("EnH", f"{resultats['EnH']:.2f} m²")

    st.markdown("**Armature détaillée** (voir onglet « Armature détaillée » pour ajuster les paramètres)")
    df_resultats_armature = pd.DataFrame([
        {"Élément": "Semelle filante — longitudinal", "Longueur (m)": resume_armature["semelle_filante"]["longitudinal_m"]},
        {"Élément": "Semelle filante — répartition", "Longueur (m)": resume_armature["semelle_filante"]["repartition_m"]},
        {"Élément": "Semelle isolée — quadrillage", "Longueur (m)": resume_armature["semelle_isolee"]["quadrillage_m"]},
        {"Élément": "Poteaux — longitudinal", "Longueur (m)": resume_armature["poteaux"]["longitudinal_m"]},
        {"Élément": "Poteaux — cadres", "Longueur (m)": resume_armature["poteaux"]["cadres_m"]},
        {"Élément": "Poutres — longitudinal", "Longueur (m)": resume_armature["poutres"]["longitudinal_m"]},
        {"Élément": "Poutres — cadres", "Longueur (m)": resume_armature["poutres"]["cadres_m"]},
        {"Élément": "Longrines — longitudinal", "Longueur (m)": resume_armature["longrines"]["longitudinal_m"]},
        {"Élément": "Longrines — cadres", "Longueur (m)": resume_armature["longrines"]["cadres_m"]},
        {"Élément": "Chaînages — longitudinal", "Longueur (m)": resume_armature["chainages"]["longitudinal_m"]},
        {"Élément": "Chaînages — cadres", "Longueur (m)": resume_armature["chainages"]["cadres_m"]},
        {"Élément": "Dalle pleine — quadrillage", "Longueur (m)": resume_armature["dalle_pleine"]["quadrillage_m"]},
    ])
    st.dataframe(df_resultats_armature, hide_index=True, use_container_width=True)

# ----------------------------------------------------------------------
# ONGLET : DEVIS
# ----------------------------------------------------------------------

with onglet_devis:
    st.subheader("Devis quantitatif de matériaux")
    c1, c2, c3 = st.columns(3)
    c1.metric("Ciment (béton)", f"{devis.total_ciment_sacs():.0f} sacs")
    c2.metric("Sable (béton)", f"{devis.quantite_sable_m3():.2f} m³")
    c3.metric("Gravier", f"{devis.quantite_gravier_m3():.2f} m³")

    st.markdown("**Agglos**")
    c1, c2, c3 = st.columns(3)
    c1.metric("Agglos", f"{devis.quantite_agglos():.0f} unités")
    c2.metric("Ciment moulage", f"{devis.ciment_moulage_agglos_sacs():.0f} sacs")
    c3.metric("Sable moulage", f"{devis.sable_moulage_agglos_m3():.2f} m³")
    c1, c2 = st.columns(2)
    c1.metric("Ciment jointement", f"{devis.ciment_jointement_mur_sacs():.0f} sacs")
    c2.metric("Sable jointement", f"{devis.sable_jointement_mur_m3():.2f} m³")

    st.markdown("**Acier des semelles — calcul simplifié (nombre de barres, 11,6 m)**")
    st.caption("Basé sur les 3 longueurs saisies dans l'onglet « Armatures ».")
    c1, c2, c3 = st.columns(3)
    c1.metric("HA6", f"{devis.nombre_barres_ha6():.0f} barres")
    c2.metric("HA8", f"{devis.nombre_barres_ha8():.0f} barres")
    c3.metric("HA10", f"{devis.nombre_barres_ha10():.0f} barres")

    st.markdown("**Acier de la structure — estimation forfaitaire (kg/m³)**")
    st.caption("Ratio 120 kg/m³ (structure) et 80 kg/m³ (dalle pleine) — ne remplace pas une note de calcul.")
    st.metric("Total acier structure", f"{devis.total_acier_structure_kg():.0f} kg")

    st.markdown("---")
    st.markdown("**Acier détaillé — tout le gros œuvre (calcul complet, onglet « Armature détaillée »)**")
    barres_devis = resume_armature["barres_par_diametre"]
    if barres_devis:
        df_barres_devis = pd.DataFrame([
            {"Diamètre": f"HA{diam}", "Longueur totale (m)": v["longueur_totale_m"],
             "Barres à commander (11,6 m)": v["nb_barres_commerciales"]}
            for diam, v in barres_devis.items()
        ])
        st.dataframe(df_barres_devis, hide_index=True, use_container_width=True)
    else:
        st.caption("Aucune donnée géométrique saisie pour l'instant (onglet Béton).")

    with st.expander("Voir le détail complet du devis"):
        st.text(devis.tableau())
