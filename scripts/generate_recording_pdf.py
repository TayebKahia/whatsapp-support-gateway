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
            Paragraph("<b>RECORDING TIPS & SYSTEM HIGHLIGHTS:</b><br/>"
                      "• <b>Phone Number Identity</b>: WhatsApp identifies callers by phone number. Customers never need to log in or create an account.<br/>"
                      "• <b>Phone Selector in Header</b>: Use the phone dropdown at the top to simulate different customers (Single Order: <code>15551234567</code>, Multi-Package: <code>15557778899</code>, New Customer: <code>15550000000</code>).<br/>"
                      "• <b>Live Telemetry Dashboard</b>: The panel on the right shows response times (under 20ms), message security checks, bot logic, and live server logs.<br/>"
                      "• <b>Real-World Customer Scenarios</b>: Single order (1-tap), multiple packages (buttons), brand-new customer, gift/cross-phone security check, PDF returns, Shopify sync, and live human handoff.<br/>"
                      "• <b>Hold Times</b>: Perform each action, then keep the screen still for the indicated seconds before clicking the next step. This makes recording voiceover easy!<br/>"
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
            "step": "STEP 0: INTRO, PHONE IDENTITY & TELEMETRY DASHBOARD",
            "duration": "16s",
            "action": "Hover mouse over WhatsApp phone on the left, point to <b>Simulated Phone</b> in the top bar, then point to the <b>Telemetry Dashboard</b> on the right.",
            "visual": "Browser at <code>localhost:8000/demo</code>. Left: WhatsApp simulator. Top: Phone presets. Right: Live dashboard showing sub-20ms speed, security checks, bot state, and real-time server logs.",
            "voice": "\"Welcome to the WhatsApp Support Gateway demo. This system lets online stores handle customer support directly on WhatsApp with zero login hassle. The bot identifies shoppers automatically by their phone number. In our top bar, you can see our phone selector, which lets us test different customer numbers. On the right, our live dashboard shows everything happening behind the scenes: lightning-fast speeds under 20 milliseconds, message security checks, bot decisions, and live server logs.\""
        },
        {
            "step": "STEP 1: SINGLE ORDER AUTO-LOOKUP (ZERO TYPING)",
            "duration": "12s",
            "action": "With simulated phone <b>15551234567</b>, click the button in the phone: <b>📦 Track Order</b> (or type <code>Track</code>).",
            "visual": "Message sent. Blue checkmarks appear, typing indicator blinks, and the bot instantly returns tracking for order #ORD-1001 with carrier (FedEx) and status (In Transit).",
            "voice": "\"When a customer taps 'Track Order' or types a message, the bot checks their phone number against the store database. Notice the blue checkmarks and typing dots. The customer never had to type an order number or search through emails—their FedEx tracking details appear in one tap in under a second.\""
        },
        {
            "step": "STEP 2: CONVERSATIONAL MEMORY & RETURN CHECK",
            "duration": "10s",
            "action": "Click chip: <b>2. Can I return it?</b> (or type <code>Can I return it?</code> in the chat input).",
            "visual": "Bot understands 'it' refers to order #ORD-1001. Because the package is still in transit, it explains that an order must be delivered first before starting a return.",
            "voice": "\"The bot has conversational memory. When the customer asks 'Can I return it?', the bot knows exactly which order they mean. Because the package is still on the delivery truck, it politely explains that an item must be delivered before it can be returned.\""
        },
        {
            "step": "STEP 3: CUSTOMER WITH MULTIPLE PACKAGES",
            "duration": "14s",
            "action": "Click purple chip: <b>📦 Demo: Multi-Package</b><br/>(or switch top dropdown to <i>Multi-Package: 15557778899</i> and tap <b>[📦 Track Order]</b>).",
            "visual": "Bot finds 2 active packages for phone +1 555-777-8899 (#ORD-1004 Fitness Watch & #ORD-1005 Soundbar). It shows clickable buttons: <b>[📦 #ORD-1004]</b> and <b>[📦 #ORD-1005]</b>.",
            "voice": "\"What happens if a customer has more than one package on the way? When we switch to a customer with multiple orders and tap 'Track Order', the bot finds both shipments automatically. Instead of getting confused, it presents simple buttons so the customer can choose which package to track.\""
        },
        {
            "step": "STEP 4: 1-TAP PACKAGE SELECTION & LIVE TRACKING",
            "duration": "10s",
            "action": "Tap the interactive button: <b>📦 #ORD-1004</b>.",
            "visual": "Bot instantly displays DHL Express tracking details and estimated delivery date for the Smart Fitness Watch.",
            "voice": "\"Tapping package 1004 immediately pulls up the live DHL tracking details and estimated arrival date, with options to return or speak to support.\""
        },
        {
            "step": "STEP 5: BRAND NEW CUSTOMER (0 ORDERS ON FILE)",
            "duration": "10s",
            "action": "In top dropdown, select: <b>New Customer (0 Orders)</b> (15550000000), click <b>🔄 Reset Session</b>, then tap <b>📦 Track Order</b>.",
            "visual": "Bot replies: 'We could not find any active orders associated with your WhatsApp number. If you placed your order under a different number or email, please reply with your order number.'",
            "voice": "\"Now, what if a brand new customer messages us? If there are no orders linked to their phone number, the bot handles it gracefully. It lets them know no orders were found and invites them to enter an order number or connect with a human agent.\""
        },
        {
            "step": "STEP 6: GIFT / DIFFERENT PHONE (PRIVACY PROTECTION)",
            "duration": "12s",
            "action": "In top dropdown, switch back to: <b>Single Order (ORD-1001)</b>.<br/>Click chip: <b>3. Track #ORD-1002 (Security Check)</b>.",
            "visual": "Customer asks for #ORD-1002, which belongs to another phone number. The security system blocks the details and asks for the last 4 digits of the phone number on that order.",
            "voice": "\"Sometimes someone buys a gift or uses a different phone to ask about an order. To prevent strangers from snooping on other people's packages, our security system steps in and asks for the last four digits of the phone number on that order.\""
        },
        {
            "step": "STEP 7: 4-DIGIT VERIFICATION UNLOCKS ORDER",
            "duration": "8s",
            "action": "Click chip: <b>4. Verify: 6543</b> (or type <code>6543</code>).",
            "visual": "Bot verifies the digits, confirms identity, and displays order #ORD-1002 status (Processing).",
            "voice": "\"When the customer types those four digits—6543—the bot confirms their identity, unlocks the order, and shows the latest status.\""
        },
        {
            "step": "STEP 8: DELIVERED RETURN & INSTANT PDF SHIPPING LABEL",
            "duration": "15s",
            "action": "Click chip <b>5. Return #ORD-1003</b>, then chip <b>6. Verify: 2233 (Get PDF)</b>.<br/>Then <b>click the PDF Document Card</b> in the phone.",
            "visual": "Order #ORD-1003 is verified as delivered. Bot approves return and attaches a downloadable PDF label. Clicking opens the vector PDF return label in a new tab with a scannable barcode and instructions.",
            "voice": "\"For delivered orders, the bot handles returns completely on autopilot. It checks return eligibility, approves it, and creates a ready-to-print return shipping label with a scannable barcode directly inside WhatsApp.\""
        },
        {
            "step": "STEP 9: LIVE SHOPIFY STORE SYNC",
            "duration": "11s",
            "action": "(Return to demo tab) Click chip: <b>7. Shopify #1001</b>.",
            "visual": "Telemetry shows data pulled via <code>ShopifyOrderAdapter</code>. Bot displays live item names, prices, and fulfillment status directly from Shopify.",
            "voice": "\"The system also connects directly to Shopify. With a single setting, it syncs live products, prices, and shipping stages straight from the store's Shopify account.\""
        },
        {
            "step": "STEP 10: HUMAN SUPPORT & AUTOMATIC BOT MUTING",
            "duration": "12s",
            "action": "Click chip: <b>8. Talk to Human</b> (or type <code>human</code>).",
            "visual": "Session state changes to amber <b>ESCALATED_HUMAN</b>. Live Operator Station opens on the right.",
            "voice": "\"Whenever a customer prefers to talk to a person, they simply type 'human' or tap the button. The bot mutes itself immediately so it won't interrupt, and opens a live support station for human agents.\""
        },
        {
            "step": "STEP 11: LIVE TWO-WAY CHAT & ZERO BOT SPAM",
            "duration": "14s",
            "action": "In phone input, type: <b>Where is my refund?</b> and send. (Notice bot stays silent).<br/>In Operator Station on right, type: <b>Hi, Agent Sarah here! Your refund of $189.50 has been released.</b> and click <b>Send as Agent</b>.",
            "visual": "Customer's message appears live in the Operator Station without any automated bot spam. Agent's reply appears in WhatsApp with an <b>Agent Sarah</b> badge.",
            "voice": "\"Notice that when the customer sends more messages, the bot stays completely quiet—no automated spam. Messages appear live on the agent's screen, and when the agent replies, their message appears instantly on the customer's phone.\""
        },
        {
            "step": "STEP 12: RESOLVING AND RE-ACTIVATING THE BOT",
            "duration": "7s",
            "action": "Click button: <b>Unmute Bot / Resolve</b>.",
            "visual": "Operator Station closes. Session state turns back to green <b>ACTIVE_BOT</b>.",
            "voice": "\"Once the customer's issue is solved, the agent clicks 'Unmute Bot'. The session returns to automated bot mode, ready for future questions.\""
        },
        {
            "step": "STEP 13: TEST SUITE & PRODUCTION RELIABILITY",
            "duration": "12s",
            "action": "Switch to terminal window and run: <b>uv run pytest</b>.",
            "visual": "All <b>103 automated tests pass green</b> in under 1.6 seconds.",
            "voice": "\"Under the hood, this is built for production reliability. Running our automated test suite shows all 103 unit and integration tests passing in under two seconds.\""
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
