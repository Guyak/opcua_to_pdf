import os
import shutil

def move_acoem_mesures(src_chemin, dest_chemin):
	## Création du dossier de destination s'il n'existe pas
	os.makedirs(dest_chemin, exist_ok=True)

	## Parcours du dossier et listing de tous les fichiers présents
	liste_fichiers = os.listdir(src_chemin)
	nb_fichiers = len(liste_fichiers)

	## Déplacement des fichiers
	for idx,nom in enumerate(liste_fichiers, start=1):
		print(f"{idx}/{nb_fichiers}", end="\r")

		# Création du lien entre les répertoires
		source = os.path.join(src_chemin, nom)
		dest = os.path.join(dest_chemin, nom)

		# Déplacement
		shutil.move(source, dest)
'''
# --- Exemple d'utilisation ---
src = f".\\test_move\\source"
dest = f".\\test_move\\dest"

move_acoem_mesures(src, dest)
'''