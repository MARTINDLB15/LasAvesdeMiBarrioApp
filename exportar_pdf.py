from fpdf import FPDF
import json
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Registros de Avistamiento de Aves', ln=True, align='C')
        self.ln(10)

def exportar_a_pdf():
    with open('registros.json', 'r', encoding='utf-8') as f:
        registros = json.load(f)

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for reg in registros:
        pdf.cell(0, 10, f"Nombre completo: {reg['nombre_completo']}", ln=True)
        pdf.cell(0, 10, f"Nombre común: {reg['nombre_comun']}", ln=True)
        pdf.cell(0, 10, f"Nombre científico: {reg['nombre_cientifico']}", ln=True)
        pdf.multi_cell(0, 10, f"Comentario: {reg['comentario']}")
        
        if reg["imagen"]:
            imagen_path = os.path.join('static', reg["imagen"])
            if os.path.exists(imagen_path):
                try:
                    pdf.image(imagen_path, w=70)
                except RuntimeError:
                    pdf.cell(0, 10, "Error al cargar imagen.", ln=True)

        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # línea separadora
        pdf.ln(10)

    pdf.output("registros_exportados.pdf")
    print("✅ PDF generado como 'registros_exportados.pdf'")

if __name__ == "__main__":
    exportar_a_pdf()