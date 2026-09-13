import io
from datetime import UTC, datetime

from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_return_label_pdf(
    order_id: str,
    customer_phone: str,
    items: list[str],
    rma_code: str,
    carrier: str = "FedEx Return Ground",
) -> bytes:
    """
    Generate an in-memory, high-resolution PDF containing a prepaid shipping label and RMA packing slip.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "LabelTitle",
        parent=styles["Heading1"],
        fontSize=14,
        leading=16,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#111827"),
    )
    meta_style = ParagraphStyle(
        "MetaText",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        fontName="Helvetica",
        textColor=colors.HexColor("#374151"),
    )
    bold_style = ParagraphStyle(
        "BoldText",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#111827"),
    )
    center_bold = ParagraphStyle(
        "CenterBold",
        parent=bold_style,
        alignment=1,
        fontSize=10,
        leading=14,
    )

    elements = []

    # 1. Carrier Header Box
    header_data = [
        [
            Paragraph(
                f"<b>{carrier.upper()}</b><br/><font size=8>PREPAID RETURN SERVICE</font>",
                title_style,
            ),
            Paragraph(
                "<b>NO POSTAGE NECESSARY<br/>IF MAILED IN THE UNITED STATES</b>",
                ParagraphStyle("Right", parent=meta_style, alignment=2),
            ),
        ]
    ]
    header_table = Table(header_data, colWidths=[340, 200])
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elements.append(header_table)
    elements.append(Spacer(1, 10))

    # 2. Addresses Box (From / Ship To)
    addr_data = [
        [
            Paragraph(
                f"<b>SHIP FROM:</b><br/>Customer Care Return<br/>Phone: {customer_phone}<br/>Order ID: #{order_id}",
                meta_style,
            ),
            Paragraph(
                "<b>SHIP TO:</b><br/><b>E-COMMERCE RETURNS DOCK 4B</b><br/>100 Logistics Parkway<br/>Memphis, TN 38118",
                meta_style,
            ),
        ]
    ]
    addr_table = Table(addr_data, colWidths=[270, 270])
    addr_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#111827")),
                ("PADDING", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9FAFB")),
            ]
        )
    )
    elements.append(addr_table)
    elements.append(Spacer(1, 14))

    # 3. Barcode Drawing
    clean_rma = rma_code.replace("#", "")
    barcode = createBarcodeDrawing(
        "Code128", value=clean_rma, width=320, height=55, humanReadable=True
    )
    elements.append(barcode)
    elements.append(Spacer(1, 8))

    # RMA Code Display
    elements.append(Paragraph(f"<b>RMA TRACKING #: {clean_rma}</b>", center_bold))
    elements.append(Spacer(1, 14))

    # 4. Cut-here Divider Line
    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#9CA3AF"),
            dash=[4, 4],
            spaceBefore=8,
            spaceAfter=14,
        )
    )
    elements.append(
        Paragraph(
            "✂ - - - - - CUT HERE AND PLACE SLIP BELOW INSIDE THE PACKAGE - - - - - ✂", center_bold
        )
    )
    elements.append(Spacer(1, 14))

    # 5. Packing Slip Section
    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    elements.append(
        Paragraph("<b>RETURN PACKING SLIP & MERCHANDISE AUTHORIZATION</b>", title_style)
    )
    elements.append(
        Paragraph(
            f"Generated: {now_str} | Order Ref: #{order_id} | RMA Code: {clean_rma}", meta_style
        )
    )
    elements.append(Spacer(1, 10))

    items_rows = [["Item Description", "Qty", "Return Status", "Eligibility"]]
    for item in items or ["Standard Order Item"]:
        items_rows.append([item, "1", "Authorized", "30-Day Window"])

    items_table = Table(items_rows, colWidths=[300, 50, 95, 95])
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
            ]
        )
    )
    elements.append(items_table)
    elements.append(Spacer(1, 14))

    # 6. Instructions
    instructions = (
        "<b>Return Instructions:</b><br/>"
        "1. Pack all authorized items securely, preferably in the original product packaging.<br/>"
        "2. Place this bottom RMA packing slip inside the box.<br/>"
        "3. Affix the top prepaid shipping label securely to the outside of the box.<br/>"
        "4. Drop off your parcel at any authorized FedEx / carrier drop-off location."
    )
    elements.append(Paragraph(instructions, meta_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
