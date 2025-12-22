from opcua import Client, ua
from json import load as j_load
from fpdf import FPDF
from rich import print as printc
from generate_pdf import *
import time
import sys
import os

##————————————————————————————————————————————————————————————————————————————##
## Extraction des fichiers de configuration
config_file = "_config_opcua.json"
with open(config_file) as file:
    credentials = j_load(file)
config_file = "_config_listes.json"
with open(config_file) as file:
    listes_param = j_load(file)

##————————————————————————————————————————————————————————————————————————————##
## Creation des dictionnaires
class Dictionnaire:
    # Cette classe crée un raccourci pour avoir une structure de code similaire au programme automate
    # dict.Toto permet d'accéder à l'item du dictionnaire dict['Toto']
    def __init__(self, data: dict):
        self._data = data
    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"Clé inconnue : {name}")
    def __setattr__(self, name, value):
        # Pour éviter de boucler sur _data
        if name == "_data":
            super().__setattr__(name, value)
        elif name in self._data:
            self._data[name] = value
        else:
            raise AttributeError(f"Impossible de créer un nouvel alias : {name}")
    def __repr__(self):
        return repr(self._data)

recette_liste = listes_param["recette_liste"]
recette = Dictionnaire(dict.fromkeys(recette_liste, -1))
rapport_liste = listes_param["rapport_liste"]
rapport = Dictionnaire(dict.fromkeys(rapport_liste, -1))

##————————————————————————————————————————————————————————————————————————————##
## Mise en place du client OPCUA
url = credentials["serveur_url"]
client = Client(url)
client.session_timeout = 30000
print(f'Connexion au serveur "{url}"...')
try:
    client.connect()
except ConnectionRefusedError:
    printc(f"[red]Connexion échouée, fermeture du programme...")
    sys.exit(1)

printc(f"[green]Connecté !\n")

##————————————————————————————————————————————————————————————————————————————##
## Lecture/Ecriture des valeurs du serveur
API_Lecture = client.get_node(f'ns=2;s=API_425056.Tags.Commande_PC.Lecture')
read_full = False

print(f"Appuyer sur CTRL-C pour arrêter le programme\n")
try:
    while True:
        if API_Lecture.get_value():
            if read_full:
                # Lecture de TOUTES les valeurs automate
                recette_filtre = recette_liste
                rapport_filtre = rapport_liste
            else:
                #Lecture uniquement pour l'essai à faire
                recette_filtre = [item for item in recette_liste if "VIDE" in item]
                rapport_filtre = [item for item in rapport_liste if "VIDE" in item]

            # Récupération des valeurs
            # Recette
            printc(f'[bright_cyan]Récupération des paramètres de recette...')
            for idx,i in enumerate(recette_filtre, start=1):
                print(f"{idx}/{len(recette_filtre)}", end="\r")
                setattr(recette, i, client.get_node(f'ns=2;s=API_425056.Tags.Recette.{i}').get_value())
            printc(f'[green]OK   ')

            # Initialisation du fichier PDF
            pdf = init_pdf("Regio2N", "MJP 250-2", "123456-789")

            # Rapport de test
            printc(f'[bright_cyan]Récupération des valeurs de rapport...')
            for idx,i in enumerate(rapport_filtre, start=1):
                print(f"{idx}/{len(rapport_filtre)}", end="\r")
                setattr(rapport, i, client.get_node(f'ns=2;s=API_425056.Tags.Rapport.{i}').get_value())
            printc(f'[green]OK   \n')

            # Affichage de valeurs - Essai à vide
            pdf = print_Vide(pdf,"Regio2N", [recette.VIDE_Vitesse_Entrainement_1, recette.VIDE_Vitesse_Entrainement_2, recette.VIDE_Vitesse_Entrainement_3],
                                            [recette.VIDE_Tension_Accept_1, recette.VIDE_Tension_Accept_2, recette.VIDE_Tension_Accept_3],
                                            [rapport.VIDE_Hyst_1, rapport.VIDE_Hyst_2, rapport.VIDE_Hyst_3],
                                            [rapport.VIDE_Tension_1, rapport.VIDE_Tension_2, rapport.VIDE_Tension_3],
                                            [True, False, True])
            printc(f"[green]Essai à vide rédigé")

            # Remise à 0 du bit de lecture
            API_Lecture.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))

            # Création de dossier basé sur le type de spécimen, la date et l'heure de l'essai
            path = f'./XXXX/{time.strftime("%Y_%m_%d")}/{time.strftime("%H_%M_%S")}'
            # Debug
            path = './Regio2N'
            if not os.path.exists(path):
                os.makedirs(path)
            # Génération du fichier PDF
            printc(f"[bright_cyan]Création du PDF au chemin {path}...")
            pdf.output(f"{path}/report.pdf")
            printc(f'[green]OK\n')
            break
except KeyboardInterrupt:
    printc(f"[bright_cyan]Arrêt du programme par l'utilisateur")
    pass

##————————————————————————————————————————————————————————————————————————————##
## Déconnexion du serveur
client.disconnect()
printc(f"[bright_cyan]Déconnecté")
