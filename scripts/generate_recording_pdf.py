from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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
            Paragraph("<b>RECORDING STRATEGY & INTERACTION MODES:</b><br/>"
                      "• <b>Dual Modes</b>: Customers can <b>click native WhatsApp buttons</b> or <b>write free-form text</b>.<br/>"
                      "• <b>Menu support</b>: Customers can tap interactive quick-reply buttons or type <code>menu</code> at any time.<br/>"
                      "• <b>Hold Time</b>: Perform each action, then pause on screen for the indicated seconds before clicking next!<br/>"
                      "• Total video runtime: <b>~2 minutes 20 seconds</b> (141 seconds).", checklist_style)
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
            "step": "STEP 0: INTRO & ARCHITECTURE",
            "duration": "14s",
            "action": "Hover mouse over WhatsApp phone on left, then live telemetry on right.",
            "visual": "Browser at <code>localhost:8000/demo</code> showing phone simulator with welcome button menu and telemetry console.",
            "voice": "\"Welcome to our WhatsApp Support Gateway demo. Built with Python and FastAPI, this system delivers sub-30ms webhook acknowledgment, secure database tool calling, and seamless live human takeover.\""
        },
        {
            "step": "STEP 1: BUTTON CLICK VS TYPING (SUB-30MS & READ RECEIPTS)",
            "duration": "12s",
            "action": "Hover over the welcome buttons, then click the native WhatsApp button: <b>📦 Track #ORD-1001</b> (or chip 1).",
            "visual": "Inbound interactive button event logged. 3 green typing dots appear, double ticks turn blue (read receipt), latency <20ms, live FedEx status returned with action buttons.",
            "voice": "\"Customers can interact however they prefer: by clicking native WhatsApp buttons and menus, or by typing natural text. Clicking our track button triggers sub-20ms acknowledgment, blue read receipts, typing dots, and live FedEx status with dynamic follow-up buttons.\""
        },
        {
            "step": "STEP 2: CONTEXT MEMORY & RETURN POLICY",
            "duration": "12s",
            "action": "Click chip: <b>2. Can I return it?</b> (or type it in the input).",
            "visual": "Bot resolves 'it' to #ORD-1001 and rejects return because shipment is in transit.",
            "voice": "\"Notice conversational context: asking 'Can I return it?' resolves 'it' to our active order. Because the package is still in transit, the bot strictly enforces return policy and explains returns require delivery first.\""
        },
        {
            "step": "STEP 3: ANTI-IDOR SECURITY CHALLENGE",
            "duration": "9s",
            "action": "Click chip: <b>3. Track #ORD-1002 (Security Check)</b>",
            "visual": "Bot intercepts query for #ORD-1002 (belongs to another phone), blocks details, and asks for last 4 digits.",
            "voice": "\"For privacy, if a customer queries someone else's order, our Anti-IDOR layer intercepts, blocks details, and demands the last 4 digits on file.\""
        },
        {
            "step": "STEP 4: OWNERSHIP AUTHENTICATION",
            "duration": "7s",
            "action": "Click chip: <b>4. Verify: 6543</b>",
            "visual": "Bot confirms 'Security Verification Successful!' and unlocks #ORD-1002 status.",
            "voice": "\"Entering the 4 digits validates ownership, unlocks the session, and presents the order status.\""
        },
        {
            "step": "STEP 5: DELIVERED ORDER RETURN REQUEST",
            "duration": "8s",
            "action": "Click chip: <b>5. Return #ORD-1003</b> (or click the button in welcome bubble).",
            "visual": "Bot detects delivered order #ORD-1003 belongs to another account and requests 4-digit verification.",
            "voice": "\"Now requesting a return on a delivered order: the gateway validates eligibility before authorizing return shipping.\""
        },
        {
            "step": "STEP 6: PROGRAMMATIC PDF RETURN LABEL & BARCODE",
            "duration": "15s",
            "action": "Click chip: <b>6. Verify: 2233 (Get PDF)</b><br/>Then <b>click the PDF Document Card</b> in phone.",
            "visual": "Bot approves return and delivers document card. Clicking opens vector PDF in new tab with Code128 barcode.",
            "voice": "\"Once verified, the gateway programmatically generates a vector PDF return shipping label using ReportLab, complete with prepaid routing, a Code128 barcode, and an RMA packing slip.\""
        },
        {
            "step": "STEP 7: SHOPIFY API INTEGRATION",
            "duration": "11s",
            "action": "(Switch back to demo tab) Click chip: <b>7. Shopify #1001</b>",
            "visual": "Telemetry shows routing via <code>ShopifyOrderAdapter</code>. Bot returns live line items and fulfillment status.",
            "voice": "\"Using clean ports and adapters, a single config flag switches from local storage to a live Shopify Admin REST API, seamlessly parsing live line items and fulfillment stages.\""
        },
        {
            "step": "STEP 8: HUMAN ESCALATION & STRICT BOT MUTING",
            "duration": "12s",
            "action": "Click chip: <b>8. Talk to Human</b> (or type <code>human</code>).",
            "visual": "Session State turns amber <b>ESCALATED_HUMAN</b>. External webhook fires. Operator Desk opens live WebSocket bridge.",
            "voice": "\"When a customer requests human help, an external webhook fires to Zendesk or n8n, strict bot muting engages, and our Operator Station opens a live WebSocket bridge.\""
        },
        {
            "step": "STEP 9: BOT MUTING VERIFICATION (ZERO SPAM)",
            "duration": "10s",
            "action": "In phone chat input, type: <b>Where is my refund?</b> and send.",
            "visual": "Message appears on phone. <b>Bot stays silent.</b> Message appears live in Operator Chat Feed on right.",
            "voice": "\"Customer follow-ups never trigger automated spam—the bot stays completely silent, while the customer's message streams live to our operator desk.\""
        },
        {
            "step": "STEP 10: REAL-TIME 2-WAY OPERATOR CHAT",
            "duration": "12s",
            "action": "In Operator Desk, type: <b>Hi, Agent Sarah here! Your refund of $189.50 has been released.</b> and click <b>Send as Agent</b>.",
            "visual": "Message appears immediately on customer phone with blue <code>👤 Agent Sarah</code> badge.",
            "voice": "\"As the human agent, typing a reply dispatches directly to the customer's WhatsApp in real time and logs to the permanent transcript.\""
        },
        {
            "step": "STEP 11: SESSION RESOLUTION",
            "duration": "7s",
            "action": "Click button: <b>Unmute Bot / Resolve</b>",
            "visual": "Operator Station closes. Session State returns to green <b>ACTIVE_BOT</b>.",
            "voice": "\"Once resolved, clicking 'Unmute Bot' re-enables automated bot handling for future inquiries.\""
        },
        {
            "step": "STEP 12: PRODUCTION RIGOR & 94 TESTS",
            "duration": "12s",
            "action": "Switch to Terminal window and run: <b>uv run pytest</b>",
            "visual": "All <b>94 tests pass green</b> in under 1.5 seconds.",
            "voice": "\"Under the hood, the system is backed by Docker Compose, Redis Streams for horizontal scaling, strict mypy typing, and 94 automated tests passing in under 1.5 seconds.\""
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
