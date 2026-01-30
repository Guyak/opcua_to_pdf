from opcua import Client, ua
from json import load as j_load
from fpdf import FPDF
from rich import print as printc
from generate_pdf import *
from csv_append import *
import time
import sys
import os

##————————————————————————————————————————————————————————————————————————————##
## Extraction des fichiers de configuration
config_file = "_config.json"
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
client.set_user(credentials["username"])
client.set_password(credentials["password"])
client.session_timeout = 30000
print(f'Connexion au serveur "{url}"...')
try:
    client.connect()
except (ConnectionRefusedError, TimeoutError):
    printc(f"[red]Connexion échouée, fermeture du programme...")
    sys.exit(1)

printc(f"[green]Connecté !\n")

##————————————————————————————————————————————————————————————————————————————##
## Lecture/Ecriture des valeurs du serveur et génération de rapport
API_Lecture = client.get_node(f'ns=2;s=API_425056.Tags.Commande_PC.Lecture')
API_Redaction_En_Cours = client.get_node(f'ns=2;s=API_425056.Tags.Commande_PC.Redaction_En_Cours')

print(f"Appuyer sur CTRL-C pour arrêter le programme\n")
printc(f'[yellow]Attente de demande d\'écriture...\n')
try:
    while True:
        if API_Lecture.get_value():
            ## Validation de la demande de rédaction
            API_Redaction_En_Cours.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))

            ##———————————————————————————————————————————————————————————————##
            ## Debug : filtre des valeurs à lire pour accélérer le programme
            read_full = True
            if read_full:
                # Lecture de TOUTES les valeurs automate
                recette_filtre = recette_liste
                rapport_filtre = rapport_liste
            else:
                #Lecture uniquement pour l'essai à faire
                recette_filtre = [item for item in recette_liste if ("GEN" in item) or ("VIBR" in item)]
                rapport_filtre = [item for item in rapport_liste if ("GEN" in item) or ("VIBR" in item)]
            ##———————————————————————————————————————————————————————————————##

            ## Récupération des valeurs
            # Recette
            printc(f'[bright_cyan]Récupération des paramètres de recette...')
            for idx,i in enumerate(recette_filtre, start=1):
                print(f"{idx}/{len(recette_filtre)}", end="\r")
                setattr(recette, i, client.get_node(f'ns=2;s=API_425056.Tags.Recette.{i}').get_value())
            printc(f'[green]OK   ')
            # Résultats
            printc(f'[bright_cyan]Récupération des résultats des essais...')
            for idx,i in enumerate(rapport_filtre, start=1):
                print(f"{idx}/{len(rapport_filtre)}", end="\r")
                setattr(rapport, i, client.get_node(f'ns=2;s=API_425056.Tags.Rapport.{i}').get_value())
            printc(f'[green]OK   \n')

            ## Création du fichier PDF
            printc(f"[bright_cyan]Rédaction du rapport...")
            # Initialisation du fichier
            pdf = init_pdf(rapport.GEN_Type_Specimen, rapport.GEN_Ref_Specimen, rapport.GEN_Symbole_Specimen, rapport.GEN_Num_Serie, rapport.GEN_Nom_Operateur, rapport.GEN_Go)
            # Rédaction des essais
            ''' 
            Parcours des essais dans l'ordre, et rédaction de l'essai correspondant par rapport à son indice
            1 : Resistances initiales à froid
            2 : Isolement
            3 : Température
            4 : Phases
            5 : Graissage
            6 : Vide
            7 : Synchro-résolveur / Capteur de vitesse
            8 : Survitesse
            9 : Vibratoire
            '''
            for idx,essai in enumerate(rapport.GEN_Ordre_Essais, start=1):
                match essai:
                    case 1:
                        # Essai de résistances à froid
                        pdf = print_RIF(pdf, idx,
                                            recette.RIF_Toler_Min, recette.RIF_Toler_Max, 
                                            rapport.RIF_Mesure_UV, rapport.RIF_Mesure_VW, rapport.RIF_Mesure_UW, rapport.RIF_Bornes_OK, 
                                            recette.RIF_Toler_Ecart, 
                                            rapport.RIF_Ecart_Max, rapport.RIF_Ecart_OK)
                        print(f"Essai de mesure des résistances initiales à froid rédigé")
                    case 2:
                        # Essai d'isolement
                        pdf = print_ISOL(pdf, idx,
                                            recette.ISOL_Bobinage_Min, rapport.ISOL_Bobinage, rapport.ISOL_Bobinage_OK,
                                            recette.ISOL_Paliers_Min, rapport.ISOL_Paliers, rapport.ISOL_Paliers_OK)
                        print(f"Essai d'isolement rédigé")
                    case 3:
                        # Essai de température
                        pdf = print_TEMP(pdf, idx,
                                            rapport.GEN_Type_Specimen, recette.TEMP_Toler_Sondes, 
                                            rapport.TEMP_Ambiante, rapport.TEMP_Specimen_1, rapport.TEMP_Specimen_2,
                                            rapport.TEMP_Go)
                        print(f"Essai de température rédigé")
                    case 4:
                        # Essai de contrôle du repérage des phases
                        pdf = print_PHASE(pdf, idx,
                                            recette.PHASE_Vitesse_Entrainement, rapport.PHASE_Go)
                        print(f"Essai de contrôle du repérage des phases rédigé")
                    case 5:
                        #Essai de graissage
                        pdf = print_GRAISS(pdf, idx,
                                            recette.GRAISS_Vitesse_Entrainement, recette.GRAISS_Tempo_Def_Graissage, 
                                            recette.GRAISS_Quantite_Palier_AV, recette.GRAISS_Quantite_Palier_AR, 
                                            rapport.GRAISS_Avant, rapport.GRAISS_Arriere, 
                                            rapport.GRAISS_Go, rapport.GRAISS_NoGo)
                        print(f"Essai de graissage rédigé")  
                    case 6:
                        # Essai à vide
                        pdf = print_VIDE(pdf, idx,
                                            rapport.GEN_Type_Specimen, [recette.VIDE_Vitesse_Entrainement_1, recette.VIDE_Vitesse_Entrainement_2, recette.VIDE_Vitesse_Entrainement_3],
                                            [recette.VIDE_Tension_Accept_1, recette.VIDE_Tension_Accept_2, recette.VIDE_Tension_Accept_3],
                                            [rapport.VIDE_Hyst_1, rapport.VIDE_Hyst_2, rapport.VIDE_Hyst_3],
                                            [rapport.VIDE_Tension_1, rapport.VIDE_Tension_2, rapport.VIDE_Tension_3],
                                            [rapport.VIDE_Tension_1_OK, rapport.VIDE_Tension_2_OK, rapport.VIDE_Tension_3_OK])
                        print(f"Essai à vide rédigé")   
                    case 7:     
                        # Essai de synchro-résolveur
                        pdf = print_SYNCHRO(pdf, idx,
                                                rapport.GEN_Type_Specimen, recette.SYNCHRO_Vitesse_Entrainement, recette.GEN_Toler_Vitesse_Entrainement,
                                                rapport.SYNCHRO_Sequence_OK, 
                                                recette.SYNCHRO_DeltaT_Min, recette.SYNCHRO_DeltaT_Max, rapport.SYNCHRO_DeltaT, rapport.SYNCHRO_DeltaT_OK,
                                                rapport.SYNCHRO_Ordre_Signaux_OK,
                                                [recette.SYNCHRO_Dephasage_Min, recette.SYNCHRO_Chevauchement_Min, recette.SYNCHRO_Duree_S1_Min, recette.SYNCHRO_Duree_S2_Min],
                                                [rapport.SYNCHRO_Dephasage, rapport.SYNCHRO_Chevauchement, rapport.SYNCHRO_Etat_1_S1, rapport.SYNCHRO_Etat_1_S2],
                                                ["---", "---", recette.SYNCHRO_Duree_S1_Max, recette.SYNCHRO_Duree_S2_Max],
                                                [rapport.SYNCHRO_Dephasage_OK, rapport.SYNCHRO_Chevauchement_OK, rapport.SYNCHRO_S1_OK, rapport.SYNCHRO_S2_OK])
                        print(f"Essai de synchro-résolveur rédigé")
                    case 8:
                        # Essai de survitesse
                        pdf = print_SURVIT(pdf, idx,
                                                recette.SURVIT_Vitesse_Entrainement, recette.SURVIT_Duree_Essai, 
                                                rapport.SURVIT_Vitesse_Arret, rapport.SURVIT_Vibr_Max, 
                                                recette.SURVIT_Limite_Vibration,
                                                rapport.SURVIT_Go, rapport.SURVIT_NoGo)
                        print(f"Essai de survitesse rédigé")
                    case 9:
                        # Essai d'analyse vibratoire
                        pdf = print_VIBR(pdf, idx,
                                            rapport.GEN_Type_Specimen, [recette.VIBR_Vitesse_Entrainement_1, recette.VIBR_Vitesse_Entrainement_2, recette.VIBR_Vitesse_Entrainement_3], 
                                            [recette.VIBR_Vibration_Max_1, recette.VIBR_Vibration_Max_2, recette.VIBR_Vibration_Max_3], 
                                            [rapport.VIBR_V_CC_1, rapport.VIBR_V_CC_2, rapport.VIBR_V_CC_3],
                                            [rapport.VIBR_V_COC_1, rapport.VIBR_V_COC_2, rapport.VIBR_V_COC_3],
                                            [rapport.VIBR_AHF_CC_1, rapport.VIBR_AHF_CC_2, rapport.VIBR_AHF_CC_3],
                                            [rapport.VIBR_AHF_COC_1, rapport.VIBR_AHF_COC_2, rapport.VIBR_AHF_COC_3],
                                            [rapport.VIBR_RL_CC_1, rapport.VIBR_RL_CC_2, rapport.VIBR_RL_CC_3],
                                            [rapport.VIBR_RL_COC_1, rapport.VIBR_RL_COC_2, rapport.VIBR_RL_COC_3],
                                            [rapport.VIBR_Mesure_1_OK, rapport.VIBR_Mesure_2_OK, rapport.VIBR_Mesure_3_OK])
                        print(f"Essai d'analyse vibratoire rédigé")
                    case _:
                        printc(f"[yellow]Dernier essai atteint")
                        break
            # Affichage de la raison de l'arrêt de l'essai en cas d'arrêt prématuré
            pdf = print_SORTIE(pdf, rapport.GEN_Entree_Etape_11, rapport.GEN_Entree_Etape_10, 
                                    rapport.GEN_Sortie_AU, rapport.GEN_Sortie_Portes, rapport.GEN_Sortie_Carter, 
                                    rapport.GEN_Sortie_Limite_Couple, recette.GEN_Limite_Couple, rapport.GEN_Sortie_Erreur_Comm)
            printc(f'[green]OK\n')

            ## Sauvegarde des paramètres dans un fichier CSV
            chemin = f'{credentials["root"]}\\{rapport.GEN_Type_Specimen}'
            os.makedirs(chemin, exist_ok=True) # exist_ok = True permet d'ignorer la commande si le dossier existe déjà
            printc(f"[bright_cyan]Remplissage du fichier CSV au chemin {chemin} ...")
            # Ajout de l'en-tête "Recette" et "Rapport" pour aider à la lecture
            dict_recette = {f"Recette.{k}": v for k, v in recette._data.items()}
            dict_rapport = {f"Rapport.{k}": v for k, v in rapport._data.items()}
            # Union des deux dictionnaires
            dict_param = dict_recette | dict_rapport
            # Appel de fonction avec exclusion des clés devant rester au début du fichier
            exclusions = ["Rapport.GEN_Type_Specimen", "Rapport.GEN_Ref_Specimen", "Rapport.GEN_Symbole_Specimen", "Rapport.GEN_Num_Serie", 
                        "Rapport.GEN_Nom_Operateur", "Rapport.GEN_Ordre_Essais", "Rapport.GEN_AUTO", "Rapport.GEN_SEMI_AUTO"]
            dict_to_csv(f'{chemin}\\datas_{rapport.GEN_Type_Specimen}.csv', dict_param, exclusions)
            printc(f'[green]OK\n')

            ## Génération du rapport
            # Création de dossier basé sur le type de spécimen, la date et l'heure de l'essai
            chemin = f'{credentials["root"]}\\{rapport.GEN_Type_Specimen}\\{rapport.GEN_Symbole_Specimen}'
            os.makedirs(chemin, exist_ok=True)
            # Génération du fichier PDF
            printc(f"[bright_cyan]Création du PDF au chemin {chemin} ...")
            # Nom du fichier : Date + Heure + Symbole Spécimen + N° Série
            nom_pdf = f'{time.strftime("%Y%m%d")}_{time.strftime("%HH%M")}_{rapport.GEN_Symbole_Specimen}_{rapport.GEN_Num_Serie}'
            # + Type d'essai (AUTO ou SEMI-AUTO)
            if rapport.GEN_AUTO:
                nom_pdf += '_AUTO'
            elif rapport.GEN_SEMI_AUTO:
                nom_pdf += '_SEMIAUTO'
            # + Résultat essai
            if rapport.GEN_Go:
                nom_pdf += 'GO'
            else:
                nom_pdf += "_NOGO"
            nom_pdf += '.pdf'
            pdf.output(f'{chemin}\\{nom_pdf}')
            printc(f'[green]OK\n')
            os.startfile(f'{chemin}\\{nom_pdf}')

            ## Remise à 0 du bit de lecture
            API_Lecture.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
            API_Redaction_En_Cours.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))

            printc(f'[yellow]Attente de demande d\'écriture...\n')
        else:
            time.sleep(1)
except KeyboardInterrupt:
    printc(f"[bright_cyan]Arrêt du programme par l'utilisateur")
    pass

##————————————————————————————————————————————————————————————————————————————##
## Déconnexion du serveur
client.disconnect()
printc(f"[bright_cyan]Déconnecté")
