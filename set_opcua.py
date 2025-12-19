from opcua import Client, ua
from json import load as j_load
import time
import sys
from rich import print as printc

##————————————————————————————————————————————————————————————————————————————##
## Extraction des fichiers de configuration
config_file = "_config_opcua.json"
with open(config_file) as file:
    credentials = j_load(file)
config_file = "_config_listes.json"
with open(config_file) as file:
    config = j_load(file)

##————————————————————————————————————————————————————————————————————————————##
## Creation des dictionnaires
class Config:
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

recette_liste = config["recette_liste"]
recette = Config(dict.fromkeys(recette_liste, -1))
rapport_liste = config["rapport_liste"]
rapport = Config(dict.fromkeys(rapport_liste, -1))

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
recette.GEN_Limite_Couple = client.get_node(f'ns=2;s=API_425056.Tags.Recette.GEN_Limite_Couple')
recette.VIDE_Tension_Accept_1 = client.get_node(f'ns=2;s=API_425056.Tags.Recette.VIDE_Tension_Accept_1')

try:
    while True:
        if API_Lecture.get_value():
            # Lecture de TOUTES les valeurs automate
            # Recette
            printc(f'[bright_cyan]Récupération des paramètres de recette...')
            for idx,i in enumerate(recette_liste, start=1):
                print(f"{idx}/{len(recette_liste)}", end="\r")
                setattr(recette, i, client.get_node(f'ns=2;s=API_425056.Tags.Recette.{i}').get_value())
            printc(f'[green]OK   ')
            # Rapport de test
            printc(f'[bright_cyan]Récupération des valeurs de rapport...')
            for idx,i in enumerate(rapport_liste, start=1):
                print(f"{idx}/{len(rapport_liste)}", end="\r")
                setattr(rapport, i, client.get_node(f'ns=2;s=API_425056.Tags.Rapport.{i}').get_value())
            printc(f'[green]OK   \n')

            # Affichage de valeurs
            print(f'{time.strftime("%Y-%m-%d_%H-%M-%S")}')
            print(f'Limite_Couple : {recette.GEN_Limite_Couple}')
            print(f'Tension_Accept_1 : {recette.VIDE_Tension_Accept_1/10}\n')

            # Remise à 0 du bit de lecture
            API_Lecture.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
except KeyboardInterrupt:
    printc(f"[bright_cyan]Arrêt du programme par l'utilisateur...")
    pass

##————————————————————————————————————————————————————————————————————————————##
## Déconnexion du serveur
client.disconnect()
printc(f"[bright_cyan]Déconnecté")
