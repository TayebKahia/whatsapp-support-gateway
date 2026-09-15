from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT_DIR = Path(__file__).parent.parent / "docs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH = OUTPUT_DIR / "DEMO_RECORDING_SCRIPT.pdf"

STATIC_PATH = Path(__file__).parent.parent / "src" / "gateway" / "static" / "demo_script.pdf"
STATIC_PATH.parent.mkdir(parents=True, exist_ok=True)

def build_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=26,
        rightMargin=26,
        topMargin=26,
        bottomMargin=26,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=3,
    )

    sub_style = ParagraphStyle(
        "DocSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10,
    )

    checklist_style = ParagraphStyle(
        "Checklist",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#065f46"),
    )

    step_title_style = ParagraphStyle(
        "StepTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#1e3a8a"),
    )

    label_action = ParagraphStyle(
        "LabelAction",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#b45309"),
    )
    text_action = ParagraphStyle(
        "TextAction",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#0f172a"),
    )

    label_visual = ParagraphStyle(
        "LabelVisual",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0369a1"),
    )
    text_visual = ParagraphStyle(
        "TextVisual",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155"),
    )

    label_voice = ParagraphStyle(
        "LabelVoice",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#047857"),
    )
    text_voice = ParagraphStyle(
        "TextVoice",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#09090b"),
    )

    # Table styles for summary
    th_style = ParagraphStyle(
        "TH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )
    td_step = ParagraphStyle(
        "TDStep",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1e3a8a"),
    )
    td_time = ParagraphStyle(
        "TDTime",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#b45309"),
        alignment=1,  # Centered
    )
    td_action = ParagraphStyle(
        "TDAction",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
    )
    td_voice = ParagraphStyle(
        "TDVoice",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
    )

    story = []

    # Title & Header
    story.append(Paragraph("WhatsApp Support Gateway - Video Recording Teleprompter", title_style))
    story.append(Paragraph("Silent-recording pacing guide with exact hold times per action for post-recording voiceover sync.", sub_style))

    # Pre-Recording Checklist Box
    checklist_data = [
        [
            Paragraph("<b>RECORDING TIPS & SYSTEM HIGHLIGHTS (UNDER 2 MINUTES):</b><br/>"
                      "• <b>Phone Number Identity</b>: WhatsApp identifies callers by phone number. Customers never need to log in or create an account.<br/>"
                      "• <b>Phone Selector in Header</b>: Use the phone dropdown at the top to simulate different customers (Single Order: <code>15551234567</code>, Multi-Package: <code>15557778899</code>, New Customer: <code>15550000000</code>).<br/>"
                      "• <b>Live Telemetry Dashboard</b>: The panel on the right shows response times (under 20ms), message security checks, bot logic, and live server logs.<br/>"
                      "• <b>Real-World Customer Scenarios</b>: Single order (1-tap), multiple packages (buttons), brand-new customer, gift/cross-phone security check, PDF returns, Shopify sync, and live human handoff.<br/>"
                      "• <b>Hold Times</b>: Perform each action, then keep the screen still for the indicated seconds before clicking the next step.<br/>"
                      "• Total video runtime: <b>~1 minute 45 seconds</b> (105 seconds).", checklist_style)
        ]
    ]
    checklist_table = Table(checklist_data, colWidths=[560])
    checklist_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ecfdf5")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#10b981")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(checklist_table)
    story.append(Spacer(1, 10))

    steps = [
        {
            "step": "STEP 0: INTRO, PHONE IDENTITY & TELEMETRY DASHBOARD",
            "duration": "10s",
            "action": "Hover mouse over phone on the left, point to <b>Simulated Phone</b> in the top bar, then point to <b>Telemetry Dashboard</b> on the right.",
            "visual": "Browser at <code>localhost:8000/demo</code>. Left: WhatsApp simulator. Top: Phone presets. Right: Live dashboard showing sub-20ms speed, security checks, bot state, and real-time server logs.",
            "voice": "\"Welcome to the WhatsApp Support Gateway demo. The system identifies customers automatically by their phone number—no logins needed. On the right, our live dashboard tracks sub-20ms speed, security, and real-time server logs.\""
        },
        {
            "step": "STEP 1: SINGLE ORDER AUTO-LOOKUP (ZERO TYPING)",
            "duration": "8s",
            "action": "With simulated phone <b>15551234567</b>, click button: <b>📦 Track Order</b> (or type <code>Track</code>).",
            "visual": "Message sent. Blue checkmarks appear, typing indicator blinks, and bot instantly returns tracking for order #ORD-1001 with FedEx tracking.",
            "voice": "\"With phone 15551234567, one tap on 'Track Order' instantly brings up FedEx tracking without typing an order number.\""
        },
        {
            "step": "STEP 2: CONVERSATIONAL MEMORY & RETURN POLICY",
            "duration": "8s",
            "action": "Click chip: <b>2. Can I return it?</b> (or type <code>Can I return it?</code>).",
            "visual": "Bot remembers order #ORD-1001. Because the package is in transit, it explains delivery is required before return.",
            "voice": "\"Asking 'Can I return it?' remembers the order. Since it's still on the truck, the bot explains it must be delivered first.\""
        },
        {
            "step": "STEP 3: MULTI-PACKAGE CUSTOMER (INTERACTIVE BUTTONS)",
            "duration": "10s",
            "action": "Click purple chip: <b>📦 Demo: Multi-Package</b>, then tap interactive button <b>[📦 #ORD-1004]</b>.",
            "visual": "Bot finds 2 active packages for phone 15557778899. Tapping #ORD-1004 instantly pulls up DHL tracking details.",
            "voice": "\"For customers with multiple orders, the bot displays clickable buttons. Tapping order ten-oh-four immediately pulls up DHL tracking.\""
        },
        {
            "step": "STEP 4: BRAND NEW CUSTOMER (0 ORDERS ON FILE)",
            "duration": "8s",
            "action": "In top dropdown, select: <b>New Customer (0 Orders)</b> (15550000000), click <b>🔄 Reset Session</b>, then tap <b>📦 Track Order</b>.",
            "visual": "Bot gracefully replies that no orders were found under this WhatsApp number and invites them to enter an order number.",
            "voice": "\"If a brand new customer reaches out with zero orders on file, the bot handles it gracefully and asks for an order number.\""
        },
        {
            "step": "STEP 5: GIFT ORDER & 4-DIGIT SECURITY PIN",
            "duration": "12s",
            "action": "In top dropdown, switch back to: <b>Single Order (ORD-1001)</b>.<br/>Click chip <b>3. Track #ORD-1002</b>, then chip <b>4. Verify: 6543</b>.",
            "visual": "Bot intercepts query for another phone's order, asks for last 4 digits. Entering 6543 confirms identity and unlocks the order status.",
            "voice": "\"If someone asks for a gift order under another phone, our security asks for the last four digits. Entering 6543 unlocks the order.\""
        },
        {
            "step": "STEP 6: DELIVERED RETURN & INSTANT PDF SHIPPING LABEL",
            "duration": "12s",
            "action": "Click chip <b>5. Return #ORD-1003</b>, chip <b>6. Verify: 2233</b>, then <b>click the PDF Card</b> in the phone.",
            "visual": "Bot verifies delivered order, approves return, and attaches a downloadable PDF label. Clicking opens the vector PDF label with a scannable barcode.",
            "voice": "\"For delivered orders, the bot approves the return and instantly generates a printable vector PDF return label with a scannable barcode.\""
        },
        {
            "step": "STEP 7: LIVE SHOPIFY STORE SYNC",
            "duration": "8s",
            "action": "(Return to demo tab) Click chip: <b>7. Shopify #1001</b>.",
            "visual": "Telemetry logs <code>ShopifyOrderAdapter</code>. Bot displays live item names, prices, and fulfillment status directly from Shopify.",
            "voice": "\"The gateway also connects to Shopify, pulling live products, prices, and shipping status straight from the store.\""
        },
        {
            "step": "STEP 8: HUMAN SUPPORT & LIVE 2-WAY CHAT",
            "duration": "14s",
            "action": "Click chip <b>8. Talk to Human</b>. In phone, type <b>Where is my refund?</b> (bot stays silent). In Operator Station, type reply and click <b>Send as Agent</b>.",
            "visual": "Bot mutes immediately. Customer's message streams to Operator Station. Agent's reply appears in WhatsApp with an <b>Agent Sarah</b> badge.",
            "voice": "\"Tapping 'Talk to Human' mutes the bot immediately to prevent spam. The customer's message streams to the operator desk, and the agent replies live.\""
        },
        {
            "step": "STEP 9: RESOLVING & UNMUTING THE BOT",
            "duration": "5s",
            "action": "Click button: <b>Unmute Bot / Resolve</b>.",
            "visual": "Operator Station closes. Session state turns back to green <b>ACTIVE_BOT</b>.",
            "voice": "\"Once solved, clicking 'Unmute Bot' re-enables automated support.\""
        },
        {
            "step": "STEP 10: PRODUCTION RIGOR & 103 AUTOMATED TESTS",
            "duration": "10s",
            "action": "Switch to terminal window and run: <b>uv run pytest</b>.",
            "visual": "All <b>103 automated tests pass green</b> in under 1.6 seconds.",
            "voice": "\"Finally, running our test suite shows all 103 automated tests passing in under two seconds.\""
        },
    ]

    for item in steps:
        header_text = f"<b>{item['step']}</b> &nbsp;&nbsp;&nbsp;&nbsp; <font color='#b45309'><b>[ ⏱️ HOLD ON SCREEN: {item['duration']} ]</b></font>"
        card_content = [
            [Paragraph(header_text, step_title_style)],
            [Paragraph("<b>👉 ACTION:</b>", label_action)],
            [Paragraph(item["action"], text_action)],
            [Paragraph("<b>👀 ON SCREEN:</b>", label_visual)],
            [Paragraph(item["visual"], text_visual)],
            [Paragraph(f"<b>🎙️ SPOKEN SCRIPT (VOICEOVER FOR THESE {item['duration']}):</b>", label_voice)],
            [Paragraph(item["voice"], text_voice)],
        ]
        t = Table(card_content, colWidths=[560])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 4.5),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('TOPPADDING', (0, 0), (-1, 0), 5),
        ]))
        story.append(KeepTogether([t, Spacer(1, 8)]))

    # Page break for the 1-page summary table
    story.append(PageBreak())
    story.append(Paragraph("Master Quick-Reference Cheat Sheet (With Wait Times)", title_style))
    story.append(Spacer(1, 8))

    summary_table_data = [
        [
            Paragraph("Action (Click / Type)", th_style),
            Paragraph("⏱️ Hold Time", th_style),
            Paragraph("What Happens on Screen", th_style),
            Paragraph("Voiceover Script (To Read Aloud)", th_style)
        ]
    ]

    for item in steps:
        summary_table_data.append([
            Paragraph(item["action"], td_action),
            Paragraph(item["duration"], td_time),
            Paragraph(item["visual"], td_step),
            Paragraph(item["voice"], td_voice)
        ])

    st = Table(summary_table_data, colWidths=[110, 45, 145, 260])
    st.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
    ]))
    story.append(st)

    doc.build(story)
    print(f"Generated PDF with hold times and button/typing features at: {PDF_PATH}")

    import shutil
    shutil.copy(PDF_PATH, STATIC_PATH)
    print(f"Copied PDF to: {STATIC_PATH}")

if __name__ == "__main__":
    build_pdf()
