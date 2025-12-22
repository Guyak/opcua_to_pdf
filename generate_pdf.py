from fpdf import FPDF
import time
import os

##————————————————————————————————————————————————————————————————————————————##
## Creation du document PDF
class PDF(FPDF):
    def __init__(self, titre, serie, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.titre = titre
        self.serie = serie

    def header(self):
        # Logo
        self.image("./_images/SNCF.png", 5,5,20)
        # Police titre
        self.set_font("helvetica", style="B", size=12)
        # Bouger le curseur à droite
        self.cell(50)
        # Titre
        self.cell(80, 5, self.titre, align="C", new_x="LEFT", new_y="NEXT")
        self.cell(80, 5, self.serie, align="C")
        # Saut de ligne
        self.ln(20)

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
        self.cell(0, 10, f"{self.serie}", align="R")

def init_pdf(type_specimen, ref_specimen, serie_specimen):
    pdf = PDF(titre=f"{type_specimen} - {ref_specimen}", serie=f"Moteur N°{serie_specimen}")
    pdf.add_font('DejaVu', '', './_fonts/DejaVuSans.ttf', uni=True)
    pdf.add_page()
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
def print_Vide(pdf, type_specimen, vitesse, tension_accep, hyst, tension, go_nogo):
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
        essai.append(str(tension[idx]))
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
        pdf.cell(go_nogo_largeur, 10, row[4], border=0, align='C')
        pdf.cell(go_nogo_largeur, 10, row[5], border=0, align='C')
        pdf.set_font("helvetica", size=12)
        pdf.ln()

    return pdf
