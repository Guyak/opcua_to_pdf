from fpdf import FPDF
import time
import os

# Définition des fonctions de création de rapport pour chaque essai
def print_Vide(pdf, type_specimen, vitesse_1, vitesse_2, vitesse_3, tension_accep_1, tension_accep_2, tension_accep_3, hyst_1, hyst_2, hyst_3, tension_1, tension_2, tension_3):
    tension_min_1 = round((tension_accep_1-hyst_1)/10, 1)
    tension_max_1 = round((tension_accep_1+hyst_1)/10, 1)
    tension_min_2 = round((tension_accep_2-hyst_2)/10, 1)
    tension_max_2 = round((tension_accep_2+hyst_2)/10, 1)
    tension_min_3 = round((tension_accep_3-hyst_3)/10, 1)
    tension_max_3 = round((tension_accep_3+hyst_3)/10, 1)

    pdf.set_font("helvetica", style="B", size=12)
    pdf.cell(0, 10, f"2 - Essai à vide", new_y="NEXT")
    pdf.set_font("helvetica", size=12)
    with pdf.table(text_align="CENTER", first_row_as_headings=False) as table:
        row = table.row()
        row.cell("Vitesse entrainement (tr/min)", rowspan=2)
        row.cell("Tension_moy. (V)", colspan=3)

        row = table.row()
        row.cell("Min")
        row.cell("Mesure")
        row.cell("Max")

        row = table.row()
        row.cell(str(vitesse_1))
        row.cell(str(tension_min_1))
        row.cell(str(tension_1))
        row.cell(str(tension_max_1))
        if type_specimen == "Regio2N":
            row = table.row()
            row.cell(str(vitesse_2))
            row.cell(str(tension_min_2))
            row.cell(str(tension_2))
            row.cell(str(tension_max_2))

            row = table.row()
            row.cell(str(vitesse_3))
            row.cell(str(tension_min_3))
            row.cell(str(tension_3))
            row.cell(str(tension_max_3))
    pdf.ln(10)
    return pdf