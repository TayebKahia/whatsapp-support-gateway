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
            Paragraph("<b>RECORDING STRATEGY & ARCHITECTURAL HIGHLIGHTS:</b><br/>"
                      "• <b>Phone-Based Identity</b>: Meta webhooks pass authenticated customer phone numbers, enabling zero-friction lookups without login.<br/>"
                      "• <b>Simulated Phone Column</b>: Point out the header selector (Single Order: <code>15551234567</code>, Multi-Package: <code>15557778899</code>, New Customer: <code>15550000000</code>).<br/>"
                      "• <b>Telemetry Cockpit</b>: Walk through sub-20ms Latency, HMAC Security, Intent Router, Session State, and Event Stream.<br/>"
                      "• <b>All 4 Order Cases</b>: Single order auto-resolution, multi-package disambiguation, new customer fallback, and cross-phone Anti-IDOR privacy shield.<br/>"
                      "• <b>Hold Time</b>: Perform each action, then pause on screen for the indicated seconds before clicking next!<br/>"
                      "• Total video runtime: <b>~2 minutes 36 seconds</b> (156 seconds).", checklist_style)
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
            "step": "STEP 0: INTRO, PHONE IDENTITY & TELEMETRY COCKPIT",
            "duration": "16s",
            "action": "Hover mouse over WhatsApp phone on left, point to <b>Simulated Phone</b> in header, then hover over the <b>Telemetry Cockpit</b> on right.",
            "visual": "Browser at <code>localhost:8000/demo</code>. Left: WhatsApp simulator. Top: Phone presets. Right: Latency (18ms), HMAC (VALID), Intent (MENU), Session State (ACTIVE_BOT), and real-time backend event stream.",
            "voice": "\"Welcome to our WhatsApp Support Gateway demo. Built with FastAPI and Python, this enterprise system eliminates login friction by using protocol-verified WhatsApp phone numbers from Meta webhooks. On the right, our live telemetry cockpit monitors sub-20ms latency, HMAC-SHA256 signature verification, deterministic intent routing, and real-time backend event logs.\""
        },
        {
            "step": "STEP 1: SINGLE ORDER AUTO-RESOLUTION (ZERO TYPING)",
            "duration": "12s",
            "action": "With simulated phone <b>15551234567</b>, click the native button in phone: <b>📦 Track Order</b>.",
            "visual": "Inbound webhook logged. Message ticks turn blue (read receipt), 3 typing dots appear, and bot immediately resolves #ORD-1001 (FedEx, in-transit) without typing an order number.",
            "voice": "\"Because Meta passes the customer's verified phone number, our gateway checks the database automatically. Notice the sub-20ms latency, blue read receipt, and typing indicator: the customer never had to type an order number—their shipment details are on screen in one tap.\""
        },
        {
            "step": "STEP 2: CONVERSATIONAL MEMORY & RETURN POLICY",
            "duration": "10s",
            "action": "Click chip: <b>2. Can I return it?</b> (or type it in the phone input).",
            "visual": "Bot resolves pronoun 'it' to #ORD-1001. Because status is 'SHIPPED', the bot strictly enforces return policy: returns require delivery first.",
            "voice": "\"Notice conversational context: asking 'Can I return it?' resolves 'it' to our active order. Because the package is still in transit, the bot enforces store policy and explains that returns require delivery first.\""
        },
        {
            "step": "STEP 3: MULTI-PACKAGE CUSTOMER (DISAMBIGUATION)",
            "duration": "14s",
            "action": "Click purple chip: <b>📦 Demo: Multi-Package</b><br/>(or switch header dropdown to <i>Multi-Package: 15557778899</i> and tap <b>[📦 Track Order]</b>).",
            "visual": "Bot detects 2 active packages for phone +1 555-777-8899 (#ORD-1004 Smart Fitness Watch & #ORD-1005 Soundbar). Displays native buttons: <b>[📦 #ORD-1004]</b> and <b>[📦 #ORD-1005]</b>.",
            "voice": "\"What if a customer ordered multiple packages? Switching to a customer with multiple active orders, the gateway automatically detects both packages and presents native interactive buttons to disambiguate with zero confusion.\""
        },
        {
            "step": "STEP 4: 1-TAP PACKAGE SELECTION & LIVE TRACKING",
            "duration": "10s",
            "action": "Tap the interactive button: <b>📦 #ORD-1004</b>.",
            "visual": "Bot instantly retrieves and displays the DHL Express tracking details and ETA for the Smart Fitness Watch.",
            "voice": "\"Tapping the package button instantly pulls up the DHL Express tracking status for that exact shipment, with follow-up action buttons attached.\""
        },
        {
            "step": "STEP 5: NEW CUSTOMER SCENARIO (0 ORDERS ON FILE)",
            "duration": "10s",
            "action": "In header dropdown, select: <b>New Customer (0 Orders)</b> (15550000000), click <b>🔄 Reset Session</b>, then tap <b>📦 Track Order</b>.",
            "visual": "Bot replies: 'We could not find any active orders associated with your WhatsApp number. If you placed your order under a different number or email, please reply with your order number.'",
            "voice": "\"If a new customer or unknown number reaches out, the gateway gracefully detects zero orders on file and prompts them for an order number in case they purchased as a gift or under an email.\""
        },
        {
            "step": "STEP 6: CROSS-PHONE ORDER & ANTI-IDOR PRIVACY SHIELD",
            "duration": "12s",
            "action": "In header dropdown, switch back to: <b>Single Order (ORD-1001)</b>.<br/>Click chip: <b>3. Track #ORD-1002 (Security Check)</b>",
            "visual": "Bot intercepts query for #ORD-1002 (registered to another phone 15559876543). Anti-IDOR security shield engages, blocks shipment details, and prompts for the last 4 digits on file.",
            "voice": "\"To prevent privacy leaks and IDOR attacks, if a customer queries an order belonging to a different phone number, our security shield intercepts the request and demands the last 4 digits of the phone number on file.\""
        },
        {
            "step": "STEP 7: PIN AUTHENTICATION UNLOCKS ORDER",
            "duration": "8s",
            "action": "Click chip: <b>4. Verify: 6543</b> (or type <code>6543</code>).",
            "visual": "Bot replies: '✅ Security Verification Successful!' and unlocks #ORD-1002 status (PROCESSING).",
            "voice": "\"Entering the 4 digits validates ownership, unlocks the session, and securely presents the order status.\""
        },
        {
            "step": "STEP 8: DELIVERED ORDER RETURN & PREPAID PDF LABEL",
            "duration": "15s",
            "action": "Click chip <b>5. Return #ORD-1003</b>, then chip <b>6. Verify: 2233 (Get PDF)</b>.<br/>Then <b>click the PDF Document Card</b> in phone.",
            "visual": "Bot verifies delivered order #ORD-1003, approves return, and attaches downloadable PDF card. Clicking opens vector PDF return label in new tab with Code128 barcode.",
            "voice": "\"For delivered orders, the bot evaluates return eligibility and programmatically generates a vector PDF shipping label using ReportLab, complete with prepaid routing, a Code128 barcode, and an RMA packing slip.\""
        },
        {
            "step": "STEP 9: SHOPIFY ADMIN API ADAPTER SYNC",
            "duration": "11s",
            "action": "(Return to demo tab) Click chip: <b>7. Shopify #1001</b>",
            "visual": "Telemetry shows routing via <code>ShopifyOrderAdapter</code>. Bot returns live line items and fulfillment status.",
            "voice": "\"Using hexagonal architecture, a single configuration switch connects our gateway to the live Shopify Admin REST API, parsing real-time line items and fulfillment stages seamlessly.\""
        },
        {
            "step": "STEP 10: HUMAN ESCALATION & STRICT BOT MUTING",
            "duration": "12s",
            "action": "Click chip: <b>8. Talk to Human</b> (or type <code>human</code>).",
            "visual": "Session State turns amber <b>ESCALATED_HUMAN</b>. Telemetry logs external webhook to Zendesk/n8n. Operator Desk opens live 2-way WebSocket bridge.",
            "voice": "\"When a customer needs human assistance, an external webhook fires to Zendesk, the bot mutes itself immediately, and our Operator Station connects via a real-time WebSocket bridge.\""
        },
        {
            "step": "STEP 11: ANTI-SPAM VERIFICATION & LIVE 2-WAY CHAT",
            "duration": "14s",
            "action": "In phone chat input, type: <b>Where is my refund?</b> and send. (Bot stays silent).<br/>In Operator Desk on right, type: <b>Hi, Agent Sarah here! Your refund of $189.50 has been released.</b> and click <b>Send as Agent</b>.",
            "visual": "Bot does NOT reply (zero spam). Customer message streams live to Operator Desk. Agent's reply dispatches directly to phone with blue <code>👤 Agent Sarah</code> badge.",
            "voice": "\"Customer follow-ups never trigger annoying bot spam—the bot stays muted while messages stream live to the operator. The agent replies directly from the console, appearing instantly on the customer's WhatsApp.\""
        },
        {
            "step": "STEP 12: SESSION RESOLUTION",
            "duration": "7s",
            "action": "Click button: <b>Unmute Bot / Resolve</b>",
            "visual": "Operator Station closes. Session State returns to green <b>ACTIVE_BOT</b>.",
            "voice": "\"Once resolved, clicking 'Unmute Bot' re-enables automated bot handling for future customer inquiries.\""
        },
        {
            "step": "STEP 13: PRODUCTION RIGOR & 103 AUTOMATED TESTS",
            "duration": "12s",
            "action": "Switch to Terminal window and run: <b>uv run pytest</b>",
            "visual": "All <b>103 tests pass green</b> in under 1.6 seconds.",
            "voice": "\"Under the hood, the system is backed by Docker Compose, Redis Streams for horizontal scaling, strict mypy typing, and 103 automated tests passing in under two seconds.\""
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
