import sys
import os

##————————————————————————————————————————————————————————————————————————————##
## Utilitaire pour fonctionnement de l'executable 
def resource_path(relative_path):
    # Récupération du chemin absolu pour fonctionnement avec PyInstaller
    try:
        # PyInstaller crée un dossier temporaire et le stocke dans _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)