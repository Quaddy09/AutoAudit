# modules/report_generator.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf_report(dataframe, filename="audit_report.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "AutoAudit - IT Audit Report")

    c.setFont("Helvetica", 10)
    y = height - 80
    for index, row in dataframe.iterrows():
        line = f"{row['Control ID']} - {row['Description']} - {row['Implemented']} - Risk: {row['Risk Score']}"
        c.drawString(50, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
