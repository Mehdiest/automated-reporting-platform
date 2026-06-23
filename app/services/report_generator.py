from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os


def generate_report(df, kpis):
    """
    Creates a simple PDF report
    """

    output_path = "reports/output.pdf"
    os.makedirs("reports", exist_ok=True)

    doc = SimpleDocTemplate(output_path)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Automated Report", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"Total Rows: {kpis['total_rows']}", styles["Normal"]))
    content.append(Paragraph(f"Total Columns: {kpis['total_columns']}", styles["Normal"]))

    if "numeric_sums" in kpis:
        content.append(Spacer(1, 12))
        content.append(Paragraph("Numeric Sums:", styles["Heading2"]))
        content.append(Paragraph(str(kpis["numeric_sums"]), styles["Normal"]))

    doc.build(content)

    return output_path