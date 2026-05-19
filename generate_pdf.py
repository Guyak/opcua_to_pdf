from fpdf import FPDF
from util_pyinstaller import *
import time
import os

##————————————————————————————————————————————————————————————————————————————##
## Creation du document PDF
class PDF(FPDF):
    def __init__(self, type=" ", reference=" ", symbole=" ", serie=" ", operateur=" ", go=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._titre = f"{type} - {reference}"
        self._symbole = f"{symbole}"
        self._serie = f"Moteur N°{serie}   "
        self._operateur = f"Etabli par : {operateur}   "
        self._go = go

    def check_break(self, hauteur_essai):
        if self.will_page_break(hauteur_essai):
            self.add_page()

    def set_font_texte(self):
        self.set_font('DejaVu', '', 10.5)

    def set_font_titre(self):
        self.set_font("helvetica", style="B", size=12)

    def set_font_case(self):
        self.set_font('DejaVu', '', 15)

    def print_go_nogo(self, statut_go, statut_nogo, hauteur):
        self.set_font_case()
        self.set_text_color(50,205,50)
        self.cell(go_nogo_largeur, hauteur, statut_go, border=0, align='C')
        self.set_text_color(255,0,0)
        self.cell(go_nogo_largeur, hauteur, statut_nogo, border=0, align='C')
        self.set_text_color(0,0,0)
        self.set_font_texte()
        self.ln()

    def header(self):
        # Logo
        y = self.get_y()
        self.image(resource_path("_images/GS.png"), 10,5,30)
        self.image(resource_path("_images/SNCF.png"), 13,20,22)
        # Police titre
        self.set_font("helvetica", style="B", size=12)
        self.set_y(y)
        # Bouger le curseur à droite
        self.cell(50)
        # Titre
        self.cell(80, 5, self._titre, align="C", new_x="LMARGIN")
        # GO/NOGO global
        self.set_font_size(24)
        if self._go :
            self.set_text_color(50,205,50)
            self.cell(0, 5, "GO  ", align="R", new_x="LMARGIN", new_y="NEXT")
        else :
            self.set_text_color(255, 0, 0)
            self.cell(0, 5, "NOGO  ", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_font_size(12)
        self.set_text_color(0, 0, 0)
        self.cell(50)
        # Symbole
        self.cell(80, 5, self._symbole, align="C", new_x="LMARGIN", new_y="NEXT")
        # Nom d'opérateur et numéro de série
        self.set_font("helvetica", size=10)
        self.set_y(23)
        self.cell(0, 5, self._operateur, align="R", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, self._serie, align="R", new_x="LMARGIN", new_y="NEXT")
        # Encadrement de l'en-tête
        self.set_y(4)
        self.cell(0, 30, "", border=1, new_x="LMARGIN", new_y="NEXT")
        # Affichage texte Go/NoGo
        self.set_font("helvetica", style="B", size=10)
        self.set_x(self.w-30)
        self.set_text_color(50,205,50)
        self.cell(10, 5, "Go", align='C')
        self.set_text_color(255,0,0)
        self.cell(10, 5, "NoGo", align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0,0,0)

    def footer(self):
        # Bouger le curseur à 1.5cm du bas de page
        self.set_y(-15)
        # Police footer
        self.set_font("helvetica", style="I", size=8)
        # Date et heure
        self.cell(0, 10, f"{time.strftime("%Y/%m/%d")} - {time.strftime("%HH%M")}", border=1, align="C")
        # Numéro de page
        self.set_y(-15)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="L")
        self.set_y(-15)
        self.cell(0, 10, f"{self._serie}", align="R")

def init_pdf(type_specimen, ref_specimen, symbole_specimen, serie_specimen, nom_operateur, go_essai):
    pdf = PDF(type=type_specimen, reference=ref_specimen, symbole=symbole_specimen, serie=serie_specimen, operateur=nom_operateur, go=go_essai)
    pdf.add_font('DejaVu', '', resource_path('_fonts/DejaVuSans.ttf'), uni=True)
    pdf.add_page()
    pdf.set_font_texte()
    return pdf

##————————————————————————————————————————————————————————————————————————————##
## Définition des fonctions de création de rapport pour chaque essai
def print_RIF(pdf, idx, res_min, res_max, res_UV, res_VW, res_UW, res_ok, ecart_toler, ecart, ecart_ok):
    ## Définition de la hauteur de l'essai, si position en bas de la page supérieure à la hauteur de l'essai => saut de page
    hauteur_essai = hauteur_texte + hauteur_multi + (hauteur_ligne*3)
    pdf.check_break(hauteur_essai)

    ## Titre
    pdf.set_font_titre()
    pdf.cell(0, hauteur_texte, f"{idx} - Mesure des résistances initiales à froid", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font_texte()

    ## Calcul de largeur des colonnes
    col_larg = [tableau_largeur*0.2, tableau_largeur*0.4, tableau_largeur*0.4]

    ## Création de l'en-tête
    # Sauvegarde des valeurs xy pour réalignement après utilisation de multi-cell
    [x, y] = [pdf.get_x(), pdf.get_y()]
    # Font DejaVu pour affichage du symbole ohm
    pdf.cell(col_larg[0], hauteur_multi, "Phase", border=1, align='C')
    pdf.cell(col_larg[1], hauteur_multi, "R à 20°C (mΩ)", border=1, align='C')
    pdf.multi_cell(col_larg[2], hauteur_multi/2, "Tolér. R à 20°C \nMin/Max (mΩ)", border=1, align='C')

    ## Mise en place des traits épais sur le tableau
    pdf.set_line_width(1.0)
    # Traits verticaux
    pdf.line(x+col_larg[0], y, x+col_larg[0], y+hauteur_multi+(hauteur_ligne*3))
    pdf.line(x+col_larg[0]+col_larg[1], y, x+col_larg[0]+col_larg[1], y+hauteur_multi+(hauteur_ligne*3))
    pdf.line(x+tableau_largeur, y, x+tableau_largeur, y+hauteur_multi+(hauteur_ligne*3))
    # Traits horizontaux
    pdf.line(x+col_larg[0], y, x+tableau_largeur, y)
    pdf.line(x+col_larg[0]+col_larg[1], y+hauteur_multi+hauteur_ligne, x+tableau_largeur, y+hauteur_multi+hauteur_ligne)
    pdf.line(x+col_larg[0], y+hauteur_multi+(hauteur_ligne*3), x+tableau_largeur, y+hauteur_multi+(hauteur_ligne*3))

    pdf.set_line_width(0.2)
    pdf.set_xy(x, y + hauteur_multi)

    ## Préparation des données
    # Création du tableau de valeurs
    data = []
    essai = ["U - V", str(res_UV), f"{res_min} / {res_max}"]
    if res_ok:
        essai.append("☑")
        essai.append("☐")
    else:
        essai.append("☐")
        essai.append("☑")
    data.append(essai)
    essai = ["V - W", str(res_VW), f"Ecart max. (%)", "", ""]
    data.append(essai)
    essai = ["U - W", str(res_UW), f"{ecart} < {ecart_toler}"]
    if ecart_ok:
        essai.append("☑")
        essai.append("☐")
    else:
        essai.append("☐")
        essai.append("☑")
    data.append(essai)

    ## Affichage des données
    for row in data:
        # Colonnes principales
        pdf.cell(col_larg[0], hauteur_ligne, row[0], border=1, align='C')  # UV
        pdf.cell(col_larg[1], hauteur_ligne, row[1], border=1, align='C')  # VW
        pdf.cell(col_larg[2], hauteur_ligne, row[2], border=1, align='C')  # UW

        # Colonne Go/NoGo (sans bordure, position fixe)
        pdf.set_x(go_nogo_x)
        pdf.print_go_nogo(row[3], row[4], hauteur_ligne)

    pdf.ln()
    return pdf

def print_ISOL(pdf, idx, bobinage_min, res_bobinage, bobinage_ok, paliers_min, res_paliers, paliers_ok):
    ## Définition de la hauteur de l'essai, si position en bas de la page supérieure à la hauteur de l'essai => saut de page
    hauteur_essai = hauteur_texte + (hauteur_ligne*3)
    pdf.check_break(hauteur_essai)

    ## Titre
    pdf.set_font_titre()
    pdf.cell(0, hauteur_texte, f"{idx} - Mesures d'isolement", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font_texte()

    ## Calcul de largeur des colonnes
    col_larg = [tableau_largeur / 3] * 3

    ## Création de l'en-tête
    pdf.cell(col_larg[0], hauteur_ligne, "", border=0)
    pdf.cell(col_larg[1], hauteur_ligne, "Mesure", border=1, align='C')
    pdf.cell(col_larg[2], hauteur_ligne, "Tolérance min.", border=1, align='C')
    pdf.ln()

    ## Préparation des données
    # Création du tableau de valeurs
    data = []
    essai = ["Bobinage stator", f"{res_bobinage} GΩ", f"{bobinage_min} GΩ"]
    if bobinage_ok:
        essai.append("☑")
        essai.append("☐")
    else:
        essai.append("☐")
        essai.append("☑")
    data.append(essai)
    essai = ["Paliers", f"{res_paliers} GΩ", f"{paliers_min} GΩ"]
    if paliers_ok:
        essai.append("☑")
        essai.append("☐")
    else:
        essai.append("☐")
        essai.append("☑")
    data.append(essai)

    ## Affichage des données
    for row in data:
        # Colonnes principales
        pdf.cell(col_larg[0], hauteur_ligne, row[0], border=1, align='C')  # Nom mesure
        pdf.cell(col_larg[1], hauteur_ligne, row[1], border=1, align='C')  # Mesure
        pdf.cell(col_larg[2], hauteur_ligne, row[2], border=1, align='C')  # Tolérance

        # Colonne Go/NoGo (sans bordure, position fixe)
        pdf.set_x(go_nogo_x)
        pdf.print_go_nogo(row[3], row[4], hauteur_ligne)

    pdf.set_font_texte()
    pdf.ln()
    return pdf

def print_TEMP(pdf, idx, type_specimen, temp_toler, temp_ambiante, temp_specimen_1, temp_specimen_2, go_nogo):
    ## Définition de la hauteur de l'essai, si position en bas de la page supérieure à la hauteur de l'essai => saut de page
    hauteur_essai = hauteur_texte + (hauteur_ligne*2)
    pdf.check_break(hauteur_essai)

    ## Titre
    pdf.set_font_titre()
    pdf.cell(0, hauteur_texte, f"{idx} - Sondes de température", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font_texte()

    ## Calcul de largeur des colonnes
    col_larg = [tableau_largeur / 4] * 4

    ## Préparation des données
    data = []
    # Création de l'entête
    titres = ["Temp. Ambiante (°C)"]
    if type_specimen == "Regio2N":
        titres.append("PT100 #1 (°C)")
        titres.append("PT100 #2 (°C)")
    else:
        titres.append("PT100 (°C)")
        titres.append(" ")
    titres.append("Tolérance max. (°C)")
    titres.append(" ") # Valeurs vides pour le Go/NoGo
    titres.append(" ") # Valeurs vides pour le Go/NoGo
    data.append(titres)

    # Mise en place des mesures
    essai = [str(temp_ambiante), str(temp_specimen_1)]
    if type_specimen == "Regio2N":
        essai.append(str(temp_specimen_2))
    else:
        essai.append(" ")
    essai.append(str(temp_toler))
    if go_nogo:
        essai.append("☑")
        essai.append("☐")
    else:
        essai.append("☐")
        essai.append("☑")
    data.append(essai)

    ## Affichage des données
    for row in data:
        # Colonnes principales
        pdf.cell(col_larg[0], hauteur_ligne, row[0], border=1, align='C')  # Temp. Ambiante
        pdf.cell(col_larg[1], hauteur_ligne, row[1], border=1, align='C')  # Temp. PT100 #1
        if type_specimen == "Regio2N":
            pdf.cell(col_larg[2], hauteur_ligne, row[2], border=1, align='C')  # Temp. PT100 #2
        pdf.cell(col_larg[3], hauteur_ligne, row[3], border=1, align='C')  # Tolérance
        # Colonne Go/NoGo (sans bordure, position fixe)
        pdf.set_x(go_nogo_x)
        pdf.print_go_nogo(row[4], row[5], hauteur_ligne)

    pdf.ln()
    return pdf

def print_PHASE(pdf, idx, vitesse, go_nogo):
    ## Définition de la hauteur de l'essai, si position en bas de la page supérieure à la hauteur de l'essai => saut de page
    hauteur_essai = (hauteur_texte*3) + (hauteur_ligne*3)
    pdf.check_break(hauteur_essai)

    ## Titre
    pdf.set_font_titre()
    pdf.cell(0, hauteur_texte, f"{idx} - Contrôle du repérage des phases", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font_texte()

    ## Affichage des paramètres de l'essai
    # Calcul de largeur des colonnes
    col_larg = [tableau_largeur*0.2] + [tableau_largeur*0.2] + [tableau_largeur*0.05] + [tableau_largeur*0.1] + [tableau_largeur*0.05] + [tableau_largeur*0.2] + [tableau_largeur*0.2]

    pdf.cell(0, hauteur_texte, f"Entrainement du spécimen à {vitesse} tr/min en sens horaire vu côté bout d'arbre.", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, hauteur_texte, f"Vérification automatique du repérage via relais de contrôle du sens de rotation.")
    pdf.set_x(go_nogo_x)
    if go_nogo:
        pdf.print_go_nogo("☑", "☐", hauteur_texte)
    else:
        pdf.print_go_nogo("☐", "☑", hauteur_texte)

    ## Affichage du tableau représentant le sens de repérage des phases
    # Données
    data = []

    # Ligne 1
    row = []
    row.append("")
    row.append("1")
    row.append("⟶")
    row.append("U")
    row.append("")
    data.append(row)
    # Ligne 2
    row = []
    row.append("Contrôleur ")
    row.append("2")
    row.append("⟶")
    row.append("V")
    row.append(" Boitier spécimen")
    data.append(row)
    # Ligne 3
    row = []
    row.append("")
    row.append("3")
    row.append("⟶")
    row.append("W")
    row.append("")
    data.append(row)

    ## Dessin des données
    [x, y] = [pdf.get_x(), pdf.get_y()] # Sauvegarde de x et y pour dessin du cadre autour du boitier moteur
    pdf.set_line_width(1.0)
    # Traits verticaux
    pdf.line(x+tableau_largeur-col_larg[6], y, x+tableau_largeur-col_larg[6], y+(hauteur_ligne*3))
    pdf.line(x+col_larg[0]+col_larg[1]+col_larg[2]+col_larg[3], y, x+col_larg[0]+col_larg[1]+col_larg[2]+col_larg[3], y+(hauteur_ligne*3))
    # Traits horizontaux
    pdf.line(x+col_larg[0]+col_larg[1]+col_larg[2]+col_larg[3], y, x+tableau_largeur-col_larg[6], y)
    pdf.line(x+col_larg[0]+col_larg[1]+col_larg[2]+col_larg[3], y+(hauteur_ligne*3), x+tableau_largeur-col_larg[6], y+(hauteur_ligne*3))
    pdf.set_line_width(0.2)
    # Affichage du tableau
    for row in data:
            pdf.cell(col_larg[0], hauteur_ligne, "", border=0, align='C')  # Vide à gauche
            pdf.cell(col_larg[1], hauteur_ligne, row[0], border=0, align='R')  # "Contrôleur"
            pdf.cell(col_larg[2], hauteur_ligne, row[1], border=0, align='C')  # Numéro
            pdf.set_font("DejaVu", size=18)
            pdf.cell(col_larg[3], hauteur_ligne, row[2], border=0, align='C')  # Flèche
            pdf.set_font_texte()
            pdf.cell(col_larg[4], hauteur_ligne, row[3], border=0, align='C')  # Lettre
            pdf.cell(col_larg[5], hauteur_ligne, row[4], border=0, align='L')  # "Boitier moteur"
            pdf.ln()
    pdf.ln()
    return(pdf)

def print_GRAISS(pdf, idx, vitesse, duree_max, recette_AV, recette_AR, quantite_AV, quantite_AR, go, nogo):
    ## Définition de la hauteur de l'essai, si position en bas de la page supérieure à la hauteur de l'essai => saut de page
    hauteur_essai = (hauteur_texte*3) + (hauteur_ligne*3)
    if nogo:
        hauteur_essai += hauteur_texte
    pdf.check_break(hauteur_essai)

    ## Titre
    pdf.set_font_titre()
    pdf.cell(0, hauteur_texte, f"{idx} - Graissage", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font_texte()

    ## Calcul de largeur des colonnes
    col_larg = [tableau_largeur / 4] * 4

    ## Affichage des paramètres de l'essai
    pdf.cell(0, hauteur_texte, f"Entrainement du spécimen à {vitesse} tr/min.", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, hauteur_texte, f"Injection de graisse sur les paliers du spécimen :", new_x="LMARGIN", new_y="NEXT")

    ## Préparation des données
    data = []
    # Création de l'en-tête
    titre = ["Quantité recette (g)", "Quantité finale (g)", "Quantité recette (g)", "Quantité finale (g)", " ", " "]
    data.append(titre)
    # Insertion des valeurs
    essai = [str(recette_AV), str(quantite_AV), str(recette_AR), str(quantite_AR)]
    if go:
        essai.append("☑")
        essai.append("☐")
    else:
        essai.append("☐")
        essai.append("☑")
    data.append(essai)

    ## Affichage des données
    pdf.cell(col_larg[0]+col_larg[1], hauteur_ligne, "Palier AVANT", border=1, align='C')
    pdf.cell(col_larg[0]+col_larg[1], hauteur_ligne, "Palier ARRIERE", border=1, align='C')
    pdf.ln()
    for row in data:
        # Colonnes principales
        pdf.cell(col_larg[0], hauteur_ligne, row[0], border=1, align='C')  # Recette AV
        pdf.cell(col_larg[1], hauteur_ligne, row[1], border=1, align='C')  # Valeur AV
        pdf.cell(col_larg[2], hauteur_ligne, row[2], border=1, align='C')  # Recette AR
        pdf.cell(col_larg[3], hauteur_ligne, row[3], border=1, align='C')  # Valeur AR
        # Colonne Go/NoGo (sans bordure, position fixe)
        pdf.set_x(go_nogo_x)
        pdf.print_go_nogo(row[4], row[5], hauteur_ligne)

    if nogo:
        pdf.set_text_color(255,0,0)
        pdf.cell(0, hauteur_texte, f"Essai invalide, durée maximale d'injection de graisse ({duree_max} secondes) dépassée", border=0, align='L')
        pdf.set_text_color(0,0,0)
        pdf.ln()
    pdf.ln()
    return pdf

def print_VIDE(pdf, idx, type_specimen, vitesse, tension_accep, hyst, tension, go_nogo):
    ## Définition de la hauteur de l'essai, si position en bas de la page supérieure à la hauteur de l'essai => saut de page
    # Détermination du nombre d'essais
    if type_specimen == "Regio2N":
        n_essai = 3
    else:
        n_essai = 1
    hauteur_essai = hauteur_texte + (hauteur_ligne*(2+n_essai))
    pdf.check_break(hauteur_essai)

    ## Titre
    pdf.set_font_titre()
    pdf.cell(0, hauteur_texte, f"{idx} - Essai à vide", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font_texte()

    ## Calcul de largeur des colonnes
    col_larg = [tableau_largeur / 4] * 4

    ## Création de l'en-tête
    # Sauvegarde des valeurs xy pour réalignement après utilisation de multi-cell
    [x, y] = [pdf.get_x(), pdf.get_y()]
    pdf.multi_cell(col_larg[0], hauteur_ligne, "Entrainement \n(tr/min)", border=1, align='C')
    pdf.set_xy(x + col_larg[0], y)
    pdf.cell(col_larg[1] + col_larg[2] + col_larg[3], hauteur_ligne, "Tension moy. (V)", border=1, align='C')
    pdf.ln()
    pdf.cell(col_larg[0], hauteur_ligne, "", border=0)  # cellule vide invisible sous "Vitesse"
    for val in ["Min", "Mesure", "Max"]:
        pdf.cell(col_larg[1], hauteur_ligne, val, border=1, align='C')
    pdf.ln()

    ## Préparation des données 
    # Calcul des valeurs min et max à afficher
    tension_min = []
    tension_max = []
    for idx in range(3):
        tension_min.append(round((tension_accep[idx]-hyst[idx]), 1))
        tension_max.append(round((tension_accep[idx]+hyst[idx]), 1))
    
    # Préparation des données pour chaque vitesse d'essai
    data = []
    for idx in range(n_essai):
        essai = []
        essai.append(str(vitesse[idx]))
        essai.append(str(tension_min[idx]))
        essai.append(str(tension[idx]))
        essai.append(str(tension_max[idx]))
        if go_nogo[idx]:
            essai.append("☑")
            essai.append("☐")
        else:
            essai.append("☐")
            essai.append("☑")
        data.append(essai)

    ## Création du tableau
    for row in data:
        # Colonnes principales
        pdf.cell(col_larg[0], hauteur_ligne, row[0], border=1, align='C')  # Vitesse
        pdf.cell(col_larg[1], hauteur_ligne, row[1], border=1, align='C')  # Min
        pdf.cell(col_larg[2], hauteur_ligne, row[2], border=1, align='C')  # Mesure
        pdf.cell(col_larg[3], hauteur_ligne, row[3], border=1, align='C')  # Max
        # Colonne Go/NoGo (sans bordure, position fixe)
        pdf.set_x(go_nogo_x)
        pdf.print_go_nogo(row[4], row[5], hauteur_ligne)

    pdf.ln()
    return pdf

def print_SYNCHRO(pdf, idx, type_specimen, vitesse, vitesse_toler, sequence_ok, delta_t_min, delta_t_max, delta_t, delta_t_ok, ordre_ok, min_Regiolis, mesure_Regiolis, max_Regiolis, go_nogo_Regiolis):
    ## Définition de la hauteur de l'essai, si position en bas de la page supérieure à la hauteur de l'essai => saut de page
    if type_specimen == "Regiolis MOT":
        hauteur_essai = (hauteur_texte*4) + (hauteur_ligne*6)
    else:
        hauteur_essai = (hauteur_texte*3) + (hauteur_multi*2) + hauteur_ligne
    pdf.check_break(hauteur_essai)



    ### Création du rapport pour specimen type Moteur Regiolis
    if type_specimen == "Regiolis MOT":
        ## Initialisation des rubriques pour le moteur Regiolis
        rubriques_Regiolis = ["Déphasage", "Chevauchement", "Etat 1 S1", "Etat 1 S2"]

        ## Titre
        pdf.set_font_titre()
        pdf.cell(0, hauteur_texte, f"{idx} - Contrôle de capteur de vitesse", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font_texte()

        ## Affichage consigne de vitesse d'entrainement
        pdf.cell(0, hauteur_texte, f"Vitesse d'entrainement : {vitesse} +/- {vitesse_toler} tr/min", new_x="LMARGIN", new_y="NEXT")

        ## Affichage du contrôle des séquences
        #Titre
        texte_essai = "Contrôle de l'ordre des signaux :         S1 à 1"
        pdf.cell(pdf.get_string_width(texte_essai), hauteur_texte, texte_essai, border=0, align='L')

        # Dessin de flèche entre les deux zones de texte
        [x, y] = [pdf.get_x(), pdf.get_y()]
        [x_0, y_0, x_1] = [x+4, y+(hauteur_texte/2), x+(tableau_largeur/6)-3]
        # Ligne horizontale
        pdf.line(x_0, y_0, x_1, y_0)
        # Pointe de flèche (triangle)
        pdf.polygon([(x_1, y_0), (x_1-4, y_0-1), (x_1-4, y_0+1)], style='DF')

        pdf.set_xy(x, y)
        pdf.cell(tableau_largeur/6, hauteur_texte, "", border=0, align='C')
        pdf.cell(tableau_largeur/4, hauteur_texte, "S2 à 1", border=0, align='L')
        # Affichage de l'état Go/NoGo
        if ordre_ok == 1:
            etat_go = "☑"
            etat_nogo = "☐"
        else:
            etat_go = "☐"
            etat_nogo ="☑"
        pdf.set_x(go_nogo_x)
        pdf.print_go_nogo(etat_go, etat_nogo, hauteur_texte)
        
        ## Affichage du contrôle de positionnement du synchro-résolveur
        # Titre
        pdf.cell(0, hauteur_texte, "Contrôle de positionnement du capteur de vitesse :", border=0, align='L', new_x="LMARGIN", new_y="NEXT")
        # En-tête du tableau
        col_larg = [tableau_largeur / 4] * 4

        pdf.cell(col_larg[0], hauteur_ligne, "", border=0)
        pdf.cell(col_larg[1] + col_larg[2] + col_larg[3], hauteur_ligne, "Valeurs temporelles (µs)", border=1, align='C')
        pdf.ln()
        pdf.cell(col_larg[0], hauteur_ligne, "", border=0)
        for val in ["Min", "Mesure", "Max"]:
            pdf.cell(col_larg[1], hauteur_ligne, val, border=1, align='C')
        pdf.ln()

        # Préparation des données
        data = []
        for idx in range(4):
            essai = []
            essai.append(str(rubriques_Regiolis[idx]))
            essai.append(str(min_Regiolis[idx]))
            essai.append(str(mesure_Regiolis[idx]))
            essai.append(str(max_Regiolis[idx]))
            if go_nogo_Regiolis[idx]:
                essai.append("☑")
                essai.append("☐")
            else:
                essai.append("☐")
                essai.append("☑")
            data.append(essai)

        for row in data:
            # Colonnes principales
            pdf.cell(col_larg[0], hauteur_ligne, row[0], border=1, align='C')  # Nom
            pdf.cell(col_larg[1], hauteur_ligne, row[1], border=1, align='C')  # Min
            pdf.cell(col_larg[2], hauteur_ligne, row[2], border=1, align='C')  # Mesure
            pdf.cell(col_larg[3], hauteur_ligne, row[3], border=1, align='C')  # Max

            # Colonne Go/NoGo (sans bordure, position fixe)
            pdf.set_x(go_nogo_x)
            pdf.print_go_nogo(row[4], row[5], hauteur_ligne)
    else:
        ## Titre
        pdf.set_font_titre()
        pdf.cell(0, hauteur_texte, f"{idx} - Contrôle du synchro-résolveur", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font_texte()

        ## Affichage consigne de vitesse d'entrainement
        pdf.cell(0, hauteur_texte, f"Vitesse d'entrainement : {vitesse} +/- {vitesse_toler} tr/min", new_x="LMARGIN", new_y="NEXT")

        ## Affichage du contrôle des séquences
        # Description
        [x, y] = [pdf.get_x(), pdf.get_y()]
        pdf.multi_cell(60, hauteur_multi/2, "Contrôle de séquence :", border=0, align='L')
        # Affichage séquences Sin-Cos
        sequences = [f"Sin < 0\nCos < 0", f"Sin < 0\nCos > 0", f"Sin > 0\nCos > 0", f"Sin > 0\nCos < 0"]
        pdf.set_xy(x + 60, y)
        x = pdf.get_x()
        for i in range(4):
            pdf.multi_cell(20, hauteur_multi/2, sequences[i], border=0, align='C')
            pdf.set_xy(x + 20, y)
            if i > 0:
                pdf.line(x, y, x, y+hauteur_multi)
            x = pdf.get_x()
        # Affichage résumé Go/NoGo
        if sequence_ok == 1:
            etat_go = "☑"
            etat_nogo = "☐"
        else:
            etat_go = "☐"
            etat_nogo ="☑"
        pdf.set_xy(go_nogo_x, y)
        pdf.print_go_nogo(etat_go, etat_nogo, hauteur_multi)

        ## Affichage du contrôle du Delta T
        # Titre
        pdf.cell(0, hauteur_texte, "Contrôle de positionnement du synchro-résolveur :", border=0, align='L', new_x="LMARGIN", new_y="NEXT")

        # En-tête
        col_larg = tableau_largeur / 2
        pdf.cell(col_larg, hauteur_multi, "Delta T (ms)", border=1, align='C')
        pdf.multi_cell(col_larg, hauteur_multi/2, f"Tolérances\nMin/Max", border=1, align='C', new_x="LMARGIN")
        # Mesure et valeurs min/max
        pdf.cell(col_larg, hauteur_ligne, str(delta_t), border=1, align='C')
        pdf.cell(col_larg, hauteur_ligne, str(f"{delta_t_min} / {delta_t_max}"), border=1, align='C')
        # Statut Go / NoGo
        pdf.set_x(go_nogo_x)
        if delta_t_ok:
            pdf.print_go_nogo("☑", "☐", hauteur_ligne)
        else:
            pdf.print_go_nogo("☐", "☑", hauteur_ligne)

    pdf.ln()
    return pdf

def print_SURVIT(pdf, idx, vitesse, duree_essai, vitesse_arret, vibration, vibration_toler, go, nogo):
    ## Définition de la hauteur de l'essai, si position en bas de la page supérieure à la hauteur de l'essai => saut de page
    hauteur_essai = (hauteur_texte*4)
    if nogo:
        hauteur_essai += hauteur_texte
    pdf.check_break(hauteur_essai)

    ## Titre
    pdf.set_font_titre()
    pdf.cell(0, hauteur_texte, f"{idx} - Essai de survitesse", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font_texte()

    ## Affichage des paramètres de l'essai
    pdf.cell(0, hauteur_texte, f"Entrainement du spécimen à {vitesse} tr/min pendant {duree_essai} secondes.", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, hauteur_texte, f"Surveillance par opérateur et mesure de vibrations.")
    pdf.set_x(go_nogo_x)
    if go:
        pdf.print_go_nogo("☑", "☐", hauteur_texte)
    else:
        pdf.print_go_nogo("☐", "☑", hauteur_texte)
    pdf.cell(0, hauteur_texte, f"Vibration maximale mesurée lors de l'essai :           {vibration}     <     {vibration_toler} mm/s", border=0, align='L', new_x="LMARGIN", new_y="NEXT")
    if nogo:
        pdf.set_text_color(255,0,0)
        pdf.cell(0, hauteur_texte, f"Essai invalide, arrêt prématuré. Vitesse atteinte avant arrêt : {vitesse_arret} tr/min", border=0, align='L')
        pdf.set_text_color(0,0,0)
        pdf.ln()
    pdf.ln()
    return pdf

def print_VIBR(pdf, idx, type_specimen, vitesse, V_toler_CC, V_toler_COC, V_CC, V_COC, AHF_toler_CC, AHF_toler_COC, AHF_CC, AHF_COC, RL_toler_CC, RL_toler_COC, RL_CC, RL_COC, go_nogo_V, go_nogo_AHF, go_nogo_RL):
    ## Définition de la hauteur de l'essai, si position en bas de la page supérieure à la hauteur de l'essai => saut de page
    # Détermination du nombre d'essais
    if type_specimen == "Regiolis ALT":
        n_essai = 2
    else:
        n_essai = 3
    hauteur_essai = (hauteur_texte*3) + (hauteur_ligne*(2+(3*n_essai)))
    pdf.check_break(hauteur_essai)

    ## Titre
    pdf.set_font_titre()
    pdf.cell(0, hauteur_texte, f"{idx} - Mesure des vibrations des paliers", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font_texte()

    ## Calcul de largeur des colonnes
    col_larg = [tableau_largeur*0.23] + [tableau_largeur*0.07] + [tableau_largeur*0.175]*4

    ## Création de l'en-tête
    # Texte basique au dessus du tableau
    pdf.cell(0, hauteur_texte, "Palier vue côté bout d’arbre : CC", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, hauteur_texte, "Palier vue côté opposé bout d’arbre : COC", new_x="LMARGIN", new_y="NEXT")
    # Sauvegarde des valeurs xy pour réalignement après utilisation de multi-cell et dessin de ligne
    [x, y] = [pdf.get_x(), pdf.get_y()]

    # Dessin de lignes horizontales épaisses entre chaque vitesse
    pdf.set_line_width(0.8)

    pdf.line(x, y+(hauteur_ligne*5), x+tableau_largeur, y+(hauteur_ligne*5))
    if type_specimen != "Regiolis ALT":
        pdf.line(x, y+(hauteur_ligne*8), x+tableau_largeur, y+(hauteur_ligne*8))

    pdf.set_line_width(0.2)
    
    # Remplissage de l'entête
    pdf.multi_cell(col_larg[0] + col_larg[1], hauteur_ligne, "Entrainement \n(tr/min)", border=1, align='C')
    pdf.set_xy(x + col_larg[0] + col_larg[1], y)
    pdf.cell(col_larg[2] + col_larg[3], hauteur_ligne, "CC", border=1, align='C')
    pdf.cell(col_larg[4] + col_larg[5], hauteur_ligne, "COC", border=1, align='C')
    pdf.set_xy(x+col_larg[0] + col_larg[1], y+hauteur_ligne)
    for idx,val in enumerate(["Mesures", "Max.", "Mesures", "Max."], start=2):
        pdf.cell(col_larg[idx], hauteur_ligne, val, border=1, align='C')
    pdf.ln()
    
    ## Préparation des données 
    data = []
    for idx in range(n_essai):
        # Données V
        essai = []
        essai.append(str(vitesse[idx]))
        essai.append("V")
        essai.append(str(V_CC[idx]))
        # Si paramètre limitant = 0 => pas d'affichage (car pas de vérification)
        if V_toler_CC[idx] != 0:
            essai.append(str(V_toler_CC[idx]))
        else:
            essai.append("")
        essai.append(str(V_COC[idx]))
        # Si paramètre limitant = 0 => pas d'affichage (car pas de vérification)
        if V_toler_COC[idx] != 0:
            essai.append(str(V_toler_COC[idx]))
        else:
            essai.append("")
        if (V_toler_CC[idx] != 0) or (V_toler_COC[idx] != 0): # Si deux paramètres limitants à 0 => pas d'affichage des statuts Go/NoGo
            if go_nogo_V[idx]:
                essai.append("☑")
                essai.append("☐")
            else:
                essai.append("☐")
                essai.append("☑")
        else:
            essai.append("")
            essai.append("")
        data.append(essai)

        # Données AHF
        essai = []
        essai.append("") # Cellule vide pour décalage de la colonne vitesse
        essai.append("AHF")
        essai.append(str(AHF_CC[idx]))
        # Si paramètre limitant = 0 => pas d'affichage (car pas de vérification)
        if AHF_toler_CC[idx] != 0:
            essai.append(str(AHF_toler_CC[idx]))
        else:
            essai.append("")
        essai.append(str(AHF_COC[idx]))
        # Si paramètre limitant = 0 => pas d'affichage (car pas de vérification)
        if AHF_toler_COC[idx] != 0:
            essai.append(str(AHF_toler_COC[idx]))
        else:
            essai.append("")
        if (AHF_toler_CC[idx] != 0) or (AHF_toler_COC[idx] != 0): # Si deux paramètres limitants à 0 => pas d'affichage des statuts Go/NoGo
            if go_nogo_AHF[idx]:
                essai.append("☑")
                essai.append("☐")
            else:
                essai.append("☐")
                essai.append("☑")
        else:
            essai.append("")
            essai.append("")
        data.append(essai)

        # Données RL
        essai = []
        essai.append("") # Cellule vide pour décalage de la colonne vitesse
        essai.append("RL")
        essai.append(str(RL_CC[idx]))
        # Si paramètre limitant = 0 => pas d'affichage (car pas de vérification)
        if RL_toler_CC[idx] != 0:
            essai.append(str(RL_toler_CC[idx]))
        else:
            essai.append("")
        essai.append(str(RL_COC[idx]))
        # Si paramètre limitant = 0 => pas d'affichage (car pas de vérification)
        if RL_toler_COC[idx] != 0:
            essai.append(str(RL_toler_COC[idx]))
        else:
            essai.append("")
        if (RL_toler_CC[idx] != 0) or (RL_toler_COC[idx] != 0): # Si deux paramètres limitants à 0 => pas d'affichage des statuts Go/NoGo
            if go_nogo_RL[idx]:
                essai.append("☑")
                essai.append("☐")
            else:
                essai.append("☐")
                essai.append("☑")
        else:
            essai.append("")
            essai.append("")
        data.append(essai)

    ## Création du tableau
    for idx,row in enumerate(data, start=0):
        # Si idx multiple de 3 = Affichage de la colonne vitesse
        if idx % 3 == 0:
            pdf.cell(col_larg[0], hauteur_ligne*3, row[0], border=1, align='C')  # Vitesse
        else:
            pdf.cell(col_larg[0], hauteur_ligne, row[0], border=0, align='C')  # Vitesse vide et sans bordure
        pdf.cell(col_larg[1], hauteur_ligne, row[1], border=1, align='C')  # Intitulé de mesure
        pdf.cell(col_larg[2], hauteur_ligne, row[2], border=1, align='C')  # Valeur CC
        pdf.cell(col_larg[3], hauteur_ligne, row[3], border=1, align='C')  # Tolérance CC
        pdf.cell(col_larg[4], hauteur_ligne, row[4], border=1, align='C')  # Valeur COC
        pdf.cell(col_larg[5], hauteur_ligne, row[5], border=1, align='C')  # Tolérance COC
        # Colonne Go/NoGo (sans bordure, position fixe)
        pdf.set_x(go_nogo_x)
        pdf.print_go_nogo(row[6], row[7], hauteur_ligne)

    pdf.ln()
    return pdf

def print_SORTIE(pdf, gemma_nogo, gemma_AFCY, def_AU, def_portes, def_carter, def_couple, lim_couple, def_comm, def_general):
    if gemma_nogo:
        # Si NoGo, affichage d'un message unique
        message = f"NoGo sur le dernier essai effectué"
    elif gemma_AFCY:
        # Si perte CP, affichage du défaut spécifique
        if def_AU:
            message = f"Perte de la chaine d'arrêt d'urgence"
        elif def_portes:
            message = f"Ouverture d'une des portes de l'enceinte"
        elif def_carter:
            message = f"Ouverture du carter de protection de l'accouplement"
        elif def_couple:
            message = f"Dépassement de la limite de couple du moteur d'entrainement ({lim_couple}%)"
        elif def_comm:
            message = f"Perte de la communication d'un équipement réseau"
        elif def_general:
            message = f"Défaut général détecté sur l'automate (voir IHM)"
        else:
            message = f"Demande d'arrêt par l'opérateur"
        message += f" - Arrêt des essais"
    else:
        # Si aucune info, sortie normale du cycle, pas de message à afficher
        return pdf
        
    pdf.set_font_titre()
    pdf.set_text_color(255,0,0)
    pdf.cell(0, 10, message, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font_texte()
    pdf.set_text_color(0,0,0)

    return pdf

##————————————————————————————————————————————————————————————————————————————##
## Valeurs utiles
def util_pdf(pdf):
    # Largeur totale disponible pour la rédaction des essais
    page_largeur = pdf.w - 20
    # Largeur des colonnes réservée à la détermination des essais
    go_nogo_largeur = 10
    tableau_largeur = page_largeur - (2 * go_nogo_largeur)
    go_nogo_x = tableau_largeur + 10
    hauteur_ligne = 7
    hauteur_texte = 7
    hauteur_multi = 11
    return [page_largeur, go_nogo_largeur, tableau_largeur, go_nogo_x, hauteur_ligne, hauteur_texte, hauteur_multi]

pdf_template = PDF()
[page_largeur, go_nogo_largeur, tableau_largeur, go_nogo_x, hauteur_ligne, hauteur_texte, hauteur_multi] = util_pdf(pdf_template)