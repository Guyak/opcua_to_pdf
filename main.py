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
## Creation du document PDF
class PDF(FPDF):
    def header(self):
        # Rendering logo:
        self.image("./images/SNCF.png", 5,5,20)
        # Setting font: helvetica bold 15
        self.set_font("helvetica", style="B", size=15)
        # Moving cursor to the right:
        self.cell(80)
        # Printing title:
        self.cell(30, 10, "Title", border=1, align="C")
        self.cell(20, 10, "yes", border=1)
        # Performing a line break:
        self.ln(20)

    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", style="I", size=8)
        # Printing page number:
        self.cell(0, 10, f"{time.strftime("%Y/%m/%d")}", align="C")
        self.set_y(-15)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="L")

pdf = PDF()
pdf.add_page()
pdf.set_font("helvetica", size=12)

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
print(f"Appuyer sur CTRL-C pour arrêter le programme\n")

##————————————————————————————————————————————————————————————————————————————##
## Lecture/Ecrituredes valeurs du serveur
API_Lecture = client.get_node(f'ns=2;s=API_425056.Tags.Commande_PC.Lecture')

read_full = False

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
            # Rapport de test
            printc(f'[bright_cyan]Récupération des valeurs de rapport...')
            for idx,i in enumerate(rapport_filtre, start=1):
                print(f"{idx}/{len(rapport_filtre)}", end="\r")
                setattr(rapport, i, client.get_node(f'ns=2;s=API_425056.Tags.Rapport.{i}').get_value())
            printc(f'[green]OK   \n')

            # Affichage de valeurs
            pdf = print_Vide(pdf,"Regio2N", recette.VIDE_Vitesse_Entrainement_1, recette.VIDE_Vitesse_Entrainement_2, recette.VIDE_Vitesse_Entrainement_3,
                                            recette.VIDE_Tension_Accept_1, recette.VIDE_Tension_Accept_2, recette.VIDE_Tension_Accept_3,
                                            rapport.VIDE_Hyst_1, rapport.VIDE_Hyst_2, rapport.VIDE_Hyst_3,
                                            rapport.VIDE_Tension_1, rapport.VIDE_Tension_2, rapport.VIDE_Tension_3)
            print(f"Essai à vide rédigé")

            # Remise à 0 du bit de lecture
            API_Lecture.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
except KeyboardInterrupt:
    printc(f"[bright_cyan]Arrêt du programme par l'utilisateur")
    pass

# Create report path based on specimen type, date and time
path = f'./Regiolis Mot/{time.strftime("%Y_%m_%d")}/{time.strftime("%H_%M_%S")}'
# For debug, easy path
path = './Regiolis'
if not os.path.exists(path):
    os.makedirs(path)
printc(f"[bright_cyan]Création du PDF au chemin {path}...")
pdf.output(f"{path}/report.pdf")
printc(f'[green]OK\n')

##————————————————————————————————————————————————————————————————————————————##
## Déconnexion du serveur
client.disconnect()
printc(f"[bright_cyan]Déconnecté")
