"""
Multi-Dataset Report Generator
================================
Builds a structured PDF report from multiple datasets.
Each dataset gets its own labelled section with KPI table,
followed by a consolidated summary section across all datasets.
"""

import os
import logging
from typing import Any

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)

_DEFAULT_OUTPUT_PATH = "reports/multi_report.pdf"


def _build_kpi_table(kpis: dict) -> Table:
    """
    Build a formatted ReportLab Table from a KPI dictionary.

    Args:
        kpis: Dict of KPI key-value pairs (may contain nested dicts).

    Returns:
        A styled ReportLab Table object.
    """
    rows = [["Metric", "Value"]]

    for key, value in kpis.items():
        if isinstance(value, dict):
            for sub_key, sub_val in value.items():
                rows.append([f"{key} — {sub_key}", str(sub_val)])
        else:
            rows.append([str(key).replace("_", " ").title(), str(value)])

    table = Table(rows, colWidths=[3 * inch, 3 * inch])
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2D3748")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )
    return table


def generate_multi_report(
    result: dict[str, Any],
    output_path: str = _DEFAULT_OUTPUT_PATH,
) -> str:
    """
    Generate a multi-section PDF report from processed dataset results.

    Args:
        result:      Output from multi_dataset_processor.process_multiple_datasets().
        output_path: Full path (including filename) for the output PDF.

    Returns:
        The absolute path of the generated PDF file.

    Raises:
        RuntimeError: If ReportLab fails to build the document.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    styles = getSampleStyleSheet()
    content = []

    # --- Report title ---
    content.append(Paragraph("Combined Dataset Report", styles["Title"]))
    content.append(Spacer(1, 0.1 * inch))
    content.append(Paragraph(
        f"Datasets processed: {result['dataset_count']}  |  "
        f"Total rows: {result['total_rows']}",
        styles["Normal"],
    ))
    content.append(Spacer(1, 0.2 * inch))

    # --- Per-dataset sections ---
    for i, dataset in enumerate(result["datasets"], start=1):
        content.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0")))
        content.append(Spacer(1, 0.1 * inch))
        content.append(Paragraph(f"Dataset {i}: {dataset['name']}", styles["Heading2"]))
        content.append(Paragraph(
            f"Rows: {dataset['row_count']}  |  Columns: {dataset['column_count']}",
            styles["Normal"],
        ))
        content.append(Paragraph(
            f"Fields: {', '.join(dataset['columns'])}",
            styles["Normal"],
        ))
        content.append(Spacer(1, 0.1 * inch))
        content.append(_build_kpi_table(dataset["kpis"]))
        content.append(Spacer(1, 0.2 * inch))

    # --- Merged summary section ---
    content.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2D3748")))
    content.append(Spacer(1, 0.1 * inch))
    content.append(Paragraph("Consolidated Summary (All Datasets)", styles["Heading2"]))
    content.append(Spacer(1, 0.1 * inch))
    content.append(_build_kpi_table(result["merged_kpis"]))

    # --- Skipped files (if any) ---
    if result.get("errors"):
        content.append(Spacer(1, 0.2 * inch))
        content.append(Paragraph("Skipped Files", styles["Heading3"]))
        for err in result["errors"]:
            content.append(Paragraph(
                f"• {err['file']}: {err['error']}",
                styles["Normal"],
            ))

    # --- Build PDF ---
    try:
        doc = SimpleDocTemplate(output_path)
        doc.build(content)
        logger.info("Multi-dataset report generated: %s", output_path)
    except Exception as exc:
        raise RuntimeError(f"Failed to build multi-dataset PDF report: {exc}") from exc

    return output_path
