"""
dosages.py
==========
Constantes de dosage et de ratios, utilisées par devis.py pour convertir
les volumes/surfaces de l'avant-métré en quantités de matériaux.

Valeurs mises à jour à partir du vrai fichier Excel de référence
(feuille "Devis quantitatif de matériaux"), là où elles étaient
disponibles. Le reste garde des ordres de grandeur courants.
"""

# --- Dosage en ciment, en kg par m3 de béton, selon le type d'ouvrage ---
DOSAGE_CIMENT_KG_PAR_M3 = {
    "Vbp": 150,    # béton de propreté - confirmé par le fichier de référence
    "Vbf": 300,    # béton de fondation - confirmé par le fichier de référence
    "Vbfd": 250,   # béton forme de dallage (non détaillé dans le fichier, estimation)
    "Vbst": 350,   # béton de structure (non détaillé dans le fichier, estimation)
    "Vbdp": 350,   # dalle pleine placard / cuisine (non détaillé, estimation)
    "Vpa": 300,    # poteaux amorces - hypothèse : même dosage que le béton de fondation
}

POIDS_SAC_CIMENT_KG = 50.0  # confirmé par le fichier de référence

# --- Ratios sable / gravier par m3 de béton - confirmés par le fichier de référence ---
VOLUME_SABLE_PAR_M3_BETON = 0.4
VOLUME_GRAVIER_PAR_M3_BETON = 0.8

# --- Agglos (parpaings) : nombre d'agglos par m2 de mur ---
NB_AGGLOS_PAR_M2 = 13  # confirmé par le fichier de référence (corrigé depuis 12.5)

# --- Moulage des agglos sur chantier (si non achetés tout faits) ---
NB_AGGLOS_PAR_SAC_CIMENT = 17     # confirmé par le fichier de référence
RATIO_SABLE_MOULAGE_AGGLOS = 3.5 * 0.05  # m3 de sable par sac de ciment utilisé pour le moulage

# --- Jointement des murs (mortier de pose entre agglos) ---
CIMENT_KG_PAR_M2_JOINTEMENT = 5    # confirmé par le fichier de référence
RATIO_SABLE_JOINTEMENT = 2.5 * 0.05  # m3 de sable par sac de ciment utilisé pour le jointement

# --- Acier des semelles : nombre de barres commerciales, par diamètre ---
# Le fichier de référence calcule l'acier des semelles en nombre de barres
# (longueur commerciale standard), pas en poids - contrairement au reste
# de la structure (poteaux, poutres...) où on garde un ratio kg/m3 simplifié.
LONGUEUR_BARRE_COMMERCIALE_M = 11.6
NB_BARRES_LONGITUDINALES_PAR_SEMELLE_FILANTE = 3  # facteur multiplicateur pour le HA6 longitudinal

# Poids linéaire indicatif (kg/m), pour donner un poids total informatif
POIDS_LINEAIRE_ACIER_KG_PAR_M = {
    "HA6": 0.222,
    "HA8": 0.395,
    "HA10": 0.617,
}

# --- Ratio d'acier, en kg par m3 de béton, pour les éléments où le fichier
# de référence ne détaille pas de calcul par barres (poteaux, poutres,
# chaînages, escalier, dalle pleine) ---
RATIO_ACIER_KG_PAR_M3 = {
    "Vbst": 120,   # poteaux, poutres, chaînages, escalier (moyenne, estimation)
    "Vbdp": 80,    # dalle pleine (estimation)
}
