from fpdf import FPDF
import time
import os

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


# Instantiation of inherited class
pdf = PDF()
pdf.add_page()
pdf.set_font("helvetica", size=12)
for i in range(1, 41):
    pdf.cell(0, 10, f"Printing line number {i}", new_x="LMARGIN", new_y="NEXT")

pdf.add_page()
with pdf.table(text_align="CENTER") as table:
    row = table.row()

    row = table.row()
    row.cell("Vitesse entrainement (tr/min)", rowspan=2)
    row.cell("Tension_moy. (V)", colspan=3)

    row = table.row()
    row.cell("Min")
    row.cell("Mesure")
    row.cell("Max")

    row = table.row()
    row.cell("1XXXX")
    row.cell("1MIMI")
    row.cell("1MEME")
    row.cell("1MAMA")

    row = table.row()
    row.cell("2XXXX")
    row.cell("2MIMI")
    row.cell("2MEME")
    row.cell("2MAMA")

    row = table.row()
    row.cell("3XXXX")
    row.cell("3MIMI")
    row.cell("3MEME")
    row.cell("3MAMA")

# Create report path based on specimen type, date and time
path = f'./Regiolis Mot/{time.strftime("%Y_%m_%d")}/{time.strftime("%H_%M_%S")}'
# For debug, easy path
path = './'
if not os.path.exists(path):
    os.makedirs(path)
pdf.output(f"{path}/report.pdf")