"""
conftest.py
===========
Fichier de configuration pytest. Sa seule présence à la racine du projet
suffit à ce que pytest ajoute ce dossier au chemin de recherche Python,
ce qui permet aux fichiers de tests/ de faire `from avant_metre import ...`
sans erreur d'import.
"""
