"""
donnees.py
==========
Structures de données d'entrée pour l'avant-métré.

Chaque dataclass regroupe les données de saisie d'une section du fichier
Excel d'origine (Terrassement, Béton, Agglos, Enduits...). Ces classes ne
font aucun calcul : elles ne font que stocker les valeurs saisies par
l'utilisateur, de façon structurée et validée.

On les complète section par section, dans le même ordre que le fichier
Excel de référence.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class SectionFouille:
    """Une fouille en trou (semelle isolée) : sa surface en plan et
    le nombre de fouilles identiques de ce type sur le projet."""
    surface: float   # m² (Si dans le fichier Excel)
    nombre: int      # ni


@dataclass
class DonneesTerrassement:
    """Données d'entrée de la section TERRASSEMENT du fichier Excel."""

    # Fouille en rigole (tranchée continue pour semelles filantes)
    longueur_developpee_rigole: float   # Ldfr (m)
    profondeur_rigole: float            # Ht (m)
    largeur_rigole: float               # l (m)

    # Fouilles en trous (semelles isolées), plusieurs types possibles
    fouilles_en_trous: List[SectionFouille] = field(default_factory=list)
    profondeur_fouille_trou: float = 0.0  # Htt (m), commune à tous les trous

    # Remblais
    surface_locaux: float = 0.0          # Sl (m²)
    surface_cour: float = 0.0            # Sc (m²)
    epaisseur_remblai_locaux: float = 0.0  # eprl (m)
    epaisseur_remblai_cour: float = 0.0    # eprc (m)

    # Mur de soubassement enterré (nécessaire pour Vrpf)
    hauteur_mur_sous_bassement_enterre: float = 0.0  # Htmse (m)
    epaisseur_mur_sous_bassement: float = 0.0        # Epm (m)
    longueur_developpee_mur_sous_bassement: float = 0.0  # ldms (m)


@dataclass
class SectionPoteau:
    """Un type de poteau : sa section et le nombre de poteaux identiques.

    cote_a / cote_b (m) sont optionnels et ne servent qu'au calcul détaillé
    des armatures (armature.py) : dimensions réelles de la section pour le
    périmètre des cadres. Si laissés à 0, on suppose une section carrée
    déduite de `section` (cote = racine carrée de section)."""
    section: float   # m² (Pi)
    nombre: int      # ni
    cote_a: float = 0.0
    cote_b: float = 0.0


@dataclass
class SectionPoutre:
    """Un type de poutre : sa section et sa longueur développée totale.

    largeur / hauteur (m) sont optionnels, réservés au calcul détaillé des
    armatures. Si laissés à 0, on suppose une section carrée déduite de
    `section`."""
    section: float    # m² (PPi)
    longueur: float   # m (Ld)
    largeur: float = 0.0
    hauteur: float = 0.0


@dataclass
class SectionLongrine:
    """Un type de longrine : sa section et sa longueur développée totale.

    largeur / hauteur (m) sont optionnels, réservés au calcul détaillé des
    armatures. Si laissés à 0, on suppose une section carrée déduite de
    `section`."""
    section: float    # m² (LGi)
    longueur: float   # m (Ld)
    largeur: float = 0.0
    hauteur: float = 0.0


@dataclass
class DonneesEscalier:
    """Données géométriques d'un escalier en béton."""
    hauteur_marche: float       # Htm (m)
    largeur_marche: float       # lm (m)
    emmarchement: float         # E (m) = largeur de l'escalier
    nombre_marches: int         # Nm
    longueur_paillasse: float   # Lp (m), mesurée sur la pente
    epaisseur_paillasse: float  # epp (m)
    longueur_palier: float = 0.0   # Lpr (m)
    largeur_palier: float = 0.0    # lpr (m)


@dataclass
class SectionSemelleFilante:
    """Un type de semelle filante en béton : longueur x largeur x épaisseur.
    Permet d'avoir plusieurs profils de semelle filante sur un même projet
    (ex: semelles plus épaisses sous les murs porteurs, plus fines sous
    les cloisons)."""
    longueur: float   # m
    largeur: float    # m (lbp)
    epaisseur: float  # m (epbsf)


@dataclass
class SectionSemelleIsolee:
    """Un type de semelle isolée en béton : surface x nombre x épaisseur.

    cote_x / cote_y (m) sont optionnels, réservés au calcul détaillé des
    armatures (quadrillage de la nappe inférieure). Si laissés à 0, on
    suppose une semelle carrée déduite de `surface`."""
    surface: float    # m²
    nombre: int
    epaisseur: float  # m (epbsi)
    cote_x: float = 0.0
    cote_y: float = 0.0


@dataclass
class SectionFormeDallage:
    """Une zone de forme de dallage : surface x épaisseur.
    Permet des épaisseurs différentes selon les pièces (ex: garage vs
    pièces de vie)."""
    surface: float    # m²
    epaisseur: float  # m (epbfd)


@dataclass
class DonneesBeton:
    """Données d'entrée de la section MACONNERIE - BETON du fichier Excel."""

    # Béton de propreté (suit toujours la géométrie des fouilles - une seule épaisseur)
    epaisseur_beton_proprete: float          # epbp (m)

    # Béton de fondation : plusieurs types possibles, chacun avec ses propres
    # dimensions et épaisseur
    semelles_filantes: List[SectionSemelleFilante] = field(default_factory=list)
    semelles_isolees: List[SectionSemelleIsolee] = field(default_factory=list)

    # Forme de dallage : plusieurs zones possibles, chacune avec sa propre épaisseur
    formes_dallage: List[SectionFormeDallage] = field(default_factory=list)

    # Poteaux
    hauteur_poteaux: float = 0.0             # htp (m)
    poteaux: List[SectionPoteau] = field(default_factory=list)
    poteaux: List[SectionPoteau] = field(default_factory=list)

    # Poutres et longrines
    poutres: List[SectionPoutre] = field(default_factory=list)
    longrines: List[SectionLongrine] = field(default_factory=list)

    # Chaînages
    section_chainage: float = 0.0            # (a x b) x 2, m²
    longueur_developpee_chainage: float = 0.0  # m

    # Escalier (optionnel)
    escalier: DonneesEscalier = None

    # Dalle pleine placard / paillasse cuisine
    epaisseur_dalle_pleine: float = 0.0      # eppc (m)
    longueur_placard: float = 0.0            # Lp (m)
    largeur_placard: float = 0.0             # lp (m)
    longueur_paillasse_cuisine: float = 0.0  # Lpc (m)
    largeur_paillasse_cuisine: float = 0.0   # lpc (m)

    # Poteaux amorces : tronçons de poteaux émergeant des semelles, coulés
    # avant les poteaux en élévation. Le fichier de référence donne cette
    # valeur directement (pas de formule détaillée), donc on fait pareil ici.
    volume_poteaux_amorces: float = 0.0      # Vpa (m3)


@dataclass
class DonneesAgglos:
    """Données d'entrée de la section MACONNERIE - AGGLOS du fichier Excel.

    Note : ldms (longueur développée du mur de soubassement) est déjà
    disponible dans DonneesTerrassement — pas besoin de la redéfinir ici.
    """
    hauteur_mur_soubassement: float          # Htms (m)
    longueur_developpee_mur_elevation: float  # ldme (m)
    hauteur_mur_elevation: float             # Htme (m)
    surface_baies: float = 0.0               # Sb (m²) — portes, fenêtres à déduire


@dataclass
class DonneesEnduits:
    """Données d'entrée de la section REVETEMENTS - ENDUITS du fichier Excel.

    Sme et Sm sont recalculés ici de façon indépendante (l'architecte peut
    saisir des dimensions différentes de celles de l'onglet Maçonnerie),
    plutôt que de systématiquement réutiliser les valeurs déjà calculées
    ailleurs.
    """
    # Pour le calcul indépendant de Sme (surface mur élévation) dans Enduits
    longueur_mur_elevation: float = 0.0        # m
    hauteur_mur_elevation: float = 0.0         # m
    surface_baies: float = 0.0                 # m² (portes/fenêtres à déduire)

    # Pour le calcul indépendant de Sm (portion mur soubassement hors-sol)
    longueur_mur_soubassement_hors_sol: float = 0.0  # m
    hauteur_mur_soubassement_hors_sol: float = 0.0   # m

    surface_acrotere: float = 0.0              # Sa (m²)
    surface_plancher: float = 0.0              # Sp (m²) — pour l'enduit horizontal sous plancher


@dataclass
class DonneesArmatures:
    """Longueurs développées d'armatures, pour les éléments où le devis
    de référence calcule l'acier en nombre de barres commerciales plutôt
    qu'en poids (kg). Une barre commerciale standard mesure 11,6 m.

    Conservé tel quel pour compatibilité (calcul simplifié existant dans
    devis.py). Pour un calcul détaillé couvrant tout le gros œuvre à
    partir de l'espacement des barres, voir DonneesArmaturesDetaillees
    et le module armature.py.
    """
    longueur_ha6_longitudinal_semelle_filante: float = 0.0  # Ld (m)
    longueur_ha8_transversal_semelle_filante: float = 0.0   # Ld (m)
    longueur_ha10_semelles_isolees: float = 0.0             # Ld (m)


# ----------------------------------------------------------------------
# Calcul détaillé des armatures (tout le gros œuvre)
# ----------------------------------------------------------------------
# Contrairement à DonneesArmatures ci-dessus (qui prend des longueurs déjà
# calculées en amont), les classes suivantes prennent des paramètres de
# ferraillage (nombre de barres, diamètres, espacements) et laissent
# armature.py calculer lui-même les longueurs et les recouvrements, à
# partir de la géométrie déjà saisie dans DonneesBeton (hauteurs, longueurs,
# dimensions). Objectif : ne plus faire ressaisir une longueur de fer déjà
# calculée à la main, mais calculer à partir des règles de ferraillage.

@dataclass
class FerraillageLineaire:
    """Paramètres de ferraillage communs à un type d'élément linéaire en
    béton armé (poteaux, poutres, longrines, chaînages) : armature
    longitudinale (filante) + cadres/étriers transversaux.

    cote_a / cote_b (m) ne sont utilisés que pour les chaînages, qui n'ont
    pas de liste de sections dédiée dans DonneesBeton (contrairement aux
    poteaux/poutres/longrines, dont les dimensions viennent de leurs
    propres SectionXxx)."""
    nb_barres_longitudinales: int = 4
    diametre_longitudinal_mm: int = 12
    diametre_cadre_mm: int = 6
    espacement_cadre_cm: float = 20.0
    cote_a: float = 0.0   # m, utilisé seulement pour les chaînages
    cote_b: float = 0.0   # m, utilisé seulement pour les chaînages


@dataclass
class FerraillageSemelleFilante:
    """Paramètres de ferraillage d'une semelle filante : armature
    longitudinale (dans le sens de la tranchée) + armature de répartition
    transversale (barres perpendiculaires régulièrement espacées, pas des
    cadres fermés)."""
    nb_barres_longitudinales: int = 3
    diametre_longitudinal_mm: int = 6
    diametre_repartition_mm: int = 8
    espacement_repartition_cm: float = 25.0


@dataclass
class FerraillageSemelleIsolee:
    """Paramètres de ferraillage d'une semelle isolée : quadrillage en
    nappe inférieure (même diamètre et même espacement dans les 2
    directions, hypothèse courante pour une semelle carrée ou proche)."""
    diametre_mm: int = 10
    espacement_cm: float = 15.0


@dataclass
class FerraillageDallePleine:
    """Paramètres de ferraillage d'une dalle pleine (placard, paillasse
    cuisine) : quadrillage à 2 directions, même diamètre/espacement dans
    les deux sens (hypothèse courante pour petites dalles)."""
    diametre_mm: int = 6
    espacement_cm: float = 20.0


@dataclass
class DonneesArmaturesDetaillees:
    """Paramètres de ferraillage pour le calcul détaillé de l'armature de
    tout le gros œuvre (semelles, poteaux, poutres, longrines, chaînages,
    dalle pleine). L'escalier n'est pas couvert ici : sa géométrie en
    pente rend le calcul par barres peu fiable sans plan de ferraillage
    dédié ; il reste estimé par un ratio de treillis soudé (kg/m²).

    Les valeurs par défaut sont des pratiques courantes de la profession
    (BAEL/Eurocode 2, usage France/Afrique de l'Ouest) — à faire valider
    par l'architecte ou le bureau d'études structure avant de les
    considérer comme définitives pour un projet donné.
    """
    # Enrobage : distance entre le fer et le bord du béton, dépend de
    # l'exposition (fondation = contact avec le sol, plus d'enrobage).
    enrobage_fondation_cm: float = 5.0
    enrobage_elevation_cm: float = 2.5

    # Longueur de recouvrement aux jonctions entre 2 barres commerciales :
    # exprimée comme un multiple du diamètre (règle usuelle : 50 x Ø pour
    # une adhérence courante en HA FeE500 ; à ajuster si le bureau
    # d'études impose une autre valeur).
    coefficient_recouvrement_diametre: float = 50.0

    semelle_filante: FerraillageSemelleFilante = field(default_factory=FerraillageSemelleFilante)
    semelle_isolee: FerraillageSemelleIsolee = field(default_factory=FerraillageSemelleIsolee)
    poteaux: FerraillageLineaire = field(default_factory=lambda: FerraillageLineaire(
        nb_barres_longitudinales=4, diametre_longitudinal_mm=12,
        diametre_cadre_mm=6, espacement_cadre_cm=15.0))
    poutres: FerraillageLineaire = field(default_factory=lambda: FerraillageLineaire(
        nb_barres_longitudinales=4, diametre_longitudinal_mm=12,
        diametre_cadre_mm=6, espacement_cadre_cm=20.0))
    longrines: FerraillageLineaire = field(default_factory=lambda: FerraillageLineaire(
        nb_barres_longitudinales=4, diametre_longitudinal_mm=12,
        diametre_cadre_mm=6, espacement_cadre_cm=20.0))
    chainages: FerraillageLineaire = field(default_factory=lambda: FerraillageLineaire(
        nb_barres_longitudinales=4, diametre_longitudinal_mm=10,
        diametre_cadre_mm=6, espacement_cadre_cm=20.0,
        cote_a=0.15, cote_b=0.15))
    dalle_pleine: FerraillageDallePleine = field(default_factory=FerraillageDallePleine)

    # Escalier : non calculé en détail (voir docstring de la classe),
    # estimé par un ratio de treillis soudé.
    ratio_treillis_escalier_kg_m2: float = 3.0
