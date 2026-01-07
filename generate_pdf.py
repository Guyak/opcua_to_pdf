from fpdf import FPDF
import time
import os

##————————————————————————————————————————————————————————————————————————————##
## Creation du document PDF
class PDF(FPDF):
    def __init__(self, titre, symbole, serie, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._titre = titre
        self._symbole = symbole
        self._serie = serie

    def header(self):
        # Logo
        y = self.get_y()
        self.image("./_images/GS.png", 10,5,30)
        self.image("./_images/SNCF.png", 13,20,22)
        # Police titre
        self.set_font("helvetica", style="B", size=12)
        self.set_y(y)
        # Bouger le curseur à droite
        self.cell(50)
        # Titre
        self.cell(80, 5, self._titre, align="C", new_x="LEFT", new_y="NEXT")
        self.cell(80, 5, self._symbole, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", style="B", size=10)
        self.set_y(y)
        self.cell(0, 5, self._serie, align="R", new_x="LEFT")
        # Encadrement de l'en-tête
        self.set_y(4)
        self.cell(0, 30, "", border=1, new_x="LMARGIN", new_y="NEXT")

    def footer(self):
        # Bouger le curseur à 1.5cm du bas de page
        self.set_y(-15)
        # Police footer
        self.set_font("helvetica", style="I", size=8)
        # Numéro de page
        self.cell(0, 10, f"{time.strftime("%Y/%m/%d")}", border=1, align="C")
        self.set_y(-15)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="L")
        self.set_y(-15)
        self.cell(0, 10, f"{self._serie}", align="R")

def init_pdf(type_specimen, ref_specimen, symbole_specimen, serie_specimen):
    pdf = PDF(titre=f"{type_specimen} - {ref_specimen}", symbole=f"{symbole_specimen}", serie=f"Moteur N°{serie_specimen}   ")
    pdf.add_font('DejaVu', '', './_fonts/DejaVuSans.ttf', uni=True)
    pdf.add_page()
    [page_largeur, go_nogo_largeur, tableau_largeur, go_nogo_x] = util_pdf(pdf)
    pdf.set_font("helvetica", style="B", size=10)
    pdf.set_x(go_nogo_x)
    pdf.set_text_color(50,205,50)
    pdf.cell(go_nogo_largeur, 10, "Go", border=0, align='C')
    pdf.set_text_color(255,0,0)
    pdf.cell(go_nogo_largeur, 10, "NoGo", border=0, align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0,0,0)
    pdf.set_font("helvetica", size=12)
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
    return [page_largeur, go_nogo_largeur, tableau_largeur, go_nogo_x]

##————————————————————————————————————————————————————————————————————————————##
## Définition des fonctions de création de rapport pour chaque essai
def print_VIDE(pdf, type_specimen, vitesse, tension_accep, hyst, tension, go_nogo):
    ## Récupération de valeurs utilitaires
    [page_largeur, go_nogo_largeur, tableau_largeur, go_nogo_x] = util_pdf(pdf)

    ## Titre
    pdf.set_font("helvetica", style="B", size=12)
    pdf.cell(0, 10, f"2 - Essai à vide", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", size=12)

    ## Calcul de largeur des colonnes
    col_widths = [tableau_largeur / 4] * 4

    ## Création de l'en-tête
    # Sauvegarde des valeurs xy pour réalignement après utilisation de multi-cell
    [x, y] = [pdf.get_x(), pdf.get_y()]
    pdf.multi_cell(col_widths[0], 10, "Vitesse entrainement (tr/min)", border=1, align='C')
    pdf.set_xy(x + col_widths[0], y)
    pdf.cell(col_widths[1] + col_widths[2] + col_widths[3], 10, "Tension moy. (V)", border=1, align='C')
    pdf.ln()
    pdf.cell(col_widths[0], 10, "", border=0)  # cellule vide invisible sous "Vitesse"
    for val in ["Min", "Mesure", "Max"]:
        pdf.cell(col_widths[1], 10, val, border=1, align='C')
    pdf.ln()

    ## Préparation des données 
    # Calcul des valeurs min et max à afficher
    tension_min = []
    tension_max = []
    for idx in range(3):
        tension_min.append(round((tension_accep[idx]-hyst[idx])/10, 1))
        tension_max.append(round((tension_accep[idx]+hyst[idx])/10, 1))
    
    # Préparation des données pour chaque vitesse d'essai
    if type_specimen == "Regio2N":
        n_essai = 3
    else:
        n_essai = 1
    data = []
    for idx in range(n_essai):
        essai = []
        essai.append(str(vitesse[idx]))
        essai.append(str(tension_min[idx]))
        essai.append(str(tension[idx]/10))
        essai.append(str(tension_max[idx]))
        if go_nogo[idx]:
            essai.append("☑")
            essai.append("☐")
        else:
            essai.append("☐")
            essai.append("☑")
        data.append(essai)

    # Création du tableau
    for row in data:
        # Colonnes principales
        pdf.cell(col_widths[0], 10, row[0], border=1, align='C')  # Vitesse
        pdf.cell(col_widths[1], 10, row[1], border=1, align='C')  # Min
        pdf.cell(col_widths[2], 10, row[2], border=1, align='C')  # Mesure
        pdf.cell(col_widths[3], 10, row[3], border=1, align='C')  # Max

        # Colonne Go/NoGo sans bordure, position fixe
        pdf.set_x(go_nogo_x)
        pdf.set_font('DejaVu', '', 15)
        pdf.set_text_color(50,205,50)
        pdf.cell(go_nogo_largeur, 10, row[4], border=0, align='C')
        pdf.set_text_color(255,0,0)
        pdf.cell(go_nogo_largeur, 10, row[5], border=0, align='C')
        pdf.set_text_color(0,0,0)
        pdf.set_font("helvetica", size=12)
        pdf.ln()

    pdf.ln()
    return pdf

def print_SYNCHRO(pdf, type_specimen, vitesse, toler_vitesse, sequence_ok, delta_t, delta_t_min, delta_t_max, delta_t_ok, ordre_ok, nom_Regiolis, min_Regiolis, mesure_Regiolis, max_Regiolis, go_nogo_Regiolis):
    ## Récupération de valeurs utilitaires
    [page_largeur, go_nogo_largeur, tableau_largeur, go_nogo_x] = util_pdf(pdf)

    ### Création du rapport pour specimen type Moteur Regiolis
    if type_specimen == "Regiolis MOT":
        ## Titre
        pdf.set_font("helvetica", style="B", size=12)
        pdf.cell(0, 10, f"3 - Contrôle de capteur de vitesse", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", size=12)

        ## Affichage consigne de vitesse d'entrainement
        pdf.cell(0, 10, f"Vitesse de rotation : {vitesse} +/- {toler_vitesse} tr/min", new_x="LMARGIN", new_y="NEXT")

        ## Affichage du contrôle des séquences
        #Titre
        pdf.cell(tableau_largeur, 10, "Contrôle de l'ordre des signaux :         S1 à 1 ----> S2 à 1", border=0, align='L')
        # Affichage de l'état Go/NoGo
        if ordre_ok == 1:
            etat_go = "☑"
            etat_nogo = "☐"
        else:
            etat_go = "☐"
            etat_nogo ="☑"
        pdf.set_x(go_nogo_x)
        pdf.set_font('DejaVu', '', 15)
        pdf.set_text_color(50,205,50)
        pdf.cell(go_nogo_largeur, 10, etat_go, border=0, align='C')
        pdf.set_text_color(255,0,0)
        pdf.cell(go_nogo_largeur, 10, etat_nogo, border=0, align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0,0,0)
        pdf.set_font("helvetica", size=12)
        
        ## Affichage du contrôle de positionnement du synchro-résolveur
        # Titre
        pdf.cell(0, 10, "Contrôle positionnement synchro-résolveur :", border=0, align='L', new_x="LMARGIN", new_y="NEXT")
        # En-tête du tableau
        col_widths = [tableau_largeur / 4] * 4

        pdf.cell(col_widths[0], 10, "", border=0)
        pdf.cell(col_widths[1] + col_widths[2] + col_widths[3], 10, "Valeurs temporelles (µs)", border=1, align='C')
        pdf.ln()
        pdf.cell(col_widths[0], 10, "", border=0)
        for val in ["Min", "Mesure", "Max"]:
            pdf.cell(col_widths[1], 10, val, border=1, align='C')
        pdf.ln()

        # Préparation des données
        data = []
        for idx in range(4):
            essai = []
            essai.append(str(nom_Regiolis[idx]))
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
            pdf.cell(col_widths[0], 10, row[0], border=1, align='C')  # Nom
            pdf.cell(col_widths[1], 10, row[1], border=1, align='C')  # Min
            pdf.cell(col_widths[2], 10, row[2], border=1, align='C')  # Mesure
            pdf.cell(col_widths[3], 10, row[3], border=1, align='C')  # Max

            # Colonne Go/NoGo sans bordure, position fixe
            pdf.set_x(go_nogo_x)
            pdf.set_font('DejaVu', '', 15)
            pdf.set_text_color(50,205,50)
            pdf.cell(go_nogo_largeur, 10, row[4], border=0, align='C')
            pdf.set_text_color(255,0,0)
            pdf.cell(go_nogo_largeur, 10, row[5], border=0, align='C')
            pdf.set_text_color(0,0,0)
            pdf.set_font("helvetica", size=12)
            pdf.ln()
    else:
        ## Titre
        pdf.set_font("helvetica", style="B", size=12)
        pdf.cell(0, 10, f"3 - Contrôle du synchro-résolveur", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", size=12)

        ## Affichage consigne de vitesse d'entrainement
        pdf.cell(0, 10, f"Vitesse de rotation : {vitesse} +/- {toler_vitesse} tr/min", new_x="LMARGIN", new_y="NEXT")

        ## Affichage du contrôle des séquences
        # Description
        [x, y] = [pdf.get_x(), pdf.get_y()]
        pdf.multi_cell(60, 6, "Contrôle de séquence :", border=0, align='L')
        # Affichage séquences Sin-Cos
        sequences = [f"Sin < 0\nCos < 0", f"Sin < 0\nCos > 0", f"Sin > 0\nCos > 0", f"Sin > 0\nCos < 0"]
        pdf.set_xy(x + 60, y)
        x = pdf.get_x()
        for i in range(4):
            pdf.multi_cell(20,6, sequences[i], border=0, align='C')
            pdf.set_xy(x + 20, y)
            if i > 0:
                pdf.line(x, y, x, y+12)
            x = pdf.get_x()
        # Affichage résumé Go/NoGo
        if sequence_ok == 1:
            etat_go = "☑"
            etat_nogo = "☐"
        else:
            etat_go = "☐"
            etat_nogo ="☑"
        pdf.set_xy(go_nogo_x, y)
        pdf.set_font('DejaVu', '', 15)
        pdf.set_text_color(50,205,50)
        pdf.cell(go_nogo_largeur, 12, etat_go, border=0, align='C')
        pdf.set_text_color(255,0,0)
        pdf.cell(go_nogo_largeur, 12, etat_nogo, border=0, align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0,0,0)
        pdf.set_font("helvetica", size=12)

        ## Affichage du contrôle du Delta T
        # Titre
        pdf.cell(0, 10, "Contrôle positionnement synchro-résolveur :", border=0, align='L', new_x="LMARGIN", new_y="NEXT")

        # En-tête
        col_widths = tableau_largeur / 2
        pdf.cell(col_widths, 12, "Delta T (ms)", border=1, align='C')
        pdf.multi_cell(col_widths, 6, f"Tolérances\nMin/Max", border=1, align='C', new_x="LMARGIN")
        # Mesure et valeurs min/max
        pdf.cell(col_widths, 10, str(delta_t/100), border=1, align='C')
        pdf.cell(col_widths, 10, str(f"{delta_t_min/100} / {delta_t_max/100}"), border=1, align='C')
        # Statut Go / NoGo
        pdf.set_x(go_nogo_x)
        pdf.set_font('DejaVu', '', 15)
        pdf.set_text_color(50,205,50)
        if delta_t_ok:
            pdf.cell(go_nogo_largeur, 10, "☑", border=0, align='C')
            pdf.set_text_color(255,0,0)
            pdf.cell(go_nogo_largeur, 10, "☐", border=0, align='C')
        else:
            pdf.cell(go_nogo_largeur, 10, "☐", border=0, align='C')
            pdf.set_text_color(255,0,0)
            pdf.cell(go_nogo_largeur, 10, "☑", border=0, align='C')
        pdf.set_text_color(0,0,0)
        pdf.set_font("helvetica", size=12)
        pdf.ln()

    pdf.ln()
    return pdf



