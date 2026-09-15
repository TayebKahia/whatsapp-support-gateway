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
            Paragraph("<b>4-MINUTE RECORDING GUIDE (MATCHING YOUR SCREEN RECORDING):</b><br/>"
                      "• <b>Natural & Calm Pacing</b>: You have ~15 to 30 seconds per step, giving you plenty of time to speak clearly without rushing.<br/>"
                      "• <b>Phone Number Identity</b>: WhatsApp identifies callers by phone number. Customers never need to log in or create an account.<br/>"
                      "• <b>Phone Selector in Header</b>: Use the phone dropdown at the top to simulate different customers (Single Order: <code>15551234567</code>, Multi-Package: <code>15557778899</code>, New Customer: <code>15550000000</code>).<br/>"
                      "• <b>Live Telemetry Dashboard</b>: The panel on the right shows response times (under 20ms), message security checks, bot logic, and live server logs.<br/>"
                      "• <b>Real-World Customer Scenarios</b>: Single order (1-tap), multiple packages (buttons), brand-new customer, gift/cross-phone security check, PDF returns, Shopify sync, and live human handoff.<br/>"
                      "• Total video runtime: <b>~4 minutes 10 seconds</b> (250 seconds).", checklist_style)
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
            "time_range": "0:00 - 0:25",
            "duration": "25s",
            "action": "Hover mouse over phone on the left, point to <b>Simulated Phone</b> in the top bar, then point to <b>Telemetry Dashboard</b> on the right.",
            "visual": "Browser at <code>localhost:8000/demo</code>. Left: WhatsApp simulator. Top: Phone presets. Right: Live dashboard showing sub-20ms speed, security checks, bot state, and real-time server logs.",
            "voice": "\"Hi everyone! This is my WhatsApp customer support bot for online stores. On the left, we have a phone showing WhatsApp. At the top, we can switch between different customer phone numbers to test different situations. And on the right, our live dashboard shows response speed and server logs.\""
        },
        {
            "step": "STEP 1: SINGLE ORDER AUTO-LOOKUP (ZERO TYPING)",
            "time_range": "0:25 - 0:45",
            "duration": "20s",
            "action": "With simulated phone <b>15551234567</b>, click button: <b>📦 Track Order</b> (or type <code>Track</code>).",
            "visual": "Message sent. Blue checkmarks appear, typing indicator blinks, and bot instantly returns tracking for order #ORD-1001 with FedEx tracking.",
            "voice": "\"Let's test our first customer. When they tap 'Track Order', the bot looks up their phone number right away. The customer never needs to type an order number. In less than a second, the bot finds their order and displays the FedEx tracking details.\""
        },
        {
            "step": "STEP 2: CONVERSATIONAL MEMORY & RETURN POLICY",
            "time_range": "0:45 - 1:05",
            "duration": "20s",
            "action": "Click chip: <b>2. Can I return it?</b> (or type <code>Can I return it?</code>).",
            "visual": "Bot remembers order #ORD-1001. Because the package is in transit, it explains delivery is required before return.",
            "voice": "\"Now the customer asks: 'Can I return it?' Notice that the bot remembers the order we just talked about. Since the package is still on the delivery truck, the bot explains that it must be delivered before you can return it.\""
        },
        {
            "step": "STEP 3: MULTI-PACKAGE CUSTOMER (INTERACTIVE BUTTONS)",
            "time_range": "1:05 - 1:30",
            "duration": "25s",
            "action": "Click purple chip: <b>📦 Demo: Multi-Package</b>, then tap interactive button <b>[📦 #ORD-1004]</b>.",
            "visual": "Bot finds 2 active packages for phone 15557778899. Tapping #ORD-1004 instantly pulls up live DHL tracking details.",
            "voice": "\"What if a customer ordered more than one item? Let's switch to a customer with two packages. When they tap 'Track Order', the bot shows two buttons—one for each package. The customer taps the one they want—like Order ten-oh-four—and gets the DHL tracking details right away.\""
        },
        {
            "step": "STEP 4: BRAND NEW CUSTOMER (0 ORDERS ON FILE)",
            "time_range": "1:30 - 1:55",
            "duration": "25s",
            "action": "In top dropdown, select: <b>New Customer (0 Orders)</b> (15550000000), click <b>🔄 Reset Session</b>, then tap <b>📦 Track Order</b>.",
            "visual": "Bot gracefully replies that no orders were found under this WhatsApp number and invites them to enter an order number.",
            "voice": "\"Now let's test a brand new customer who has never ordered before. When they tap 'Track Order', the bot politely says no orders were found for this number. It also asks them to type their order number in case they used a different phone when buying.\""
        },
        {
            "step": "STEP 5: GIFT ORDER & 4-DIGIT SECURITY PIN",
            "time_range": "1:55 - 2:20",
            "duration": "25s",
            "action": "In top dropdown, switch back to: <b>Single Order (ORD-1001)</b>.<br/>Click chip <b>3. Track #ORD-1002</b>, then chip <b>4. Verify: 6543</b>.",
            "visual": "Bot intercepts query for another phone's order, asks for last 4 digits. Entering 6543 confirms identity and unlocks the order status.",
            "voice": "\"What if someone bought a gift, or is using a friend's phone? If they ask for an order from another phone number, the bot protects privacy. It asks for the last four digits of the phone number on that order. When they enter six-five-four-three, the bot confirms who they are and shows the order.\""
        },
        {
            "step": "STEP 6: DELIVERED RETURN & INSTANT PDF SHIPPING LABEL",
            "time_range": "2:20 - 2:50",
            "duration": "30s",
            "action": "Click chip <b>5. Return #ORD-1003</b>, chip <b>6. Verify: 2233</b>, then <b>click the PDF Card</b> in the phone.",
            "visual": "Bot verifies delivered order, approves return, and attaches a downloadable PDF label. Clicking opens the vector PDF label with a scannable barcode.",
            "voice": "\"Next, let's look at returns. Order ten-oh-three was already delivered. So the bot approves the return immediately. It even sends a return shipping label right in the chat. When you click the card, it opens a clean PDF label with a barcode ready to print.\""
        },
        {
            "step": "STEP 7: LIVE SHOPIFY STORE SYNC",
            "time_range": "2:50 - 3:10",
            "duration": "20s",
            "action": "(Return to demo tab) Click chip: <b>7. Shopify #1001</b>.",
            "visual": "Telemetry logs <code>ShopifyOrderAdapter</code>. Bot displays live item names, prices, and fulfillment status directly from Shopify.",
            "voice": "\"The bot also connects directly to Shopify stores. Here, it pulls live product names, prices, and shipping status straight from Shopify in real time.\""
        },
        {
            "step": "STEP 8: HUMAN SUPPORT & LIVE 2-WAY CHAT",
            "time_range": "3:10 - 3:40",
            "duration": "30s",
            "action": "Click chip <b>8. Talk to Human</b>. In phone, type <b>Where is my refund?</b> (bot stays silent). In Operator Station, type reply and click <b>Send as Agent</b>.",
            "visual": "Bot mutes immediately. Customer's message streams to Operator Station. Agent's reply appears in WhatsApp with an <b>Agent Sarah</b> badge.",
            "voice": "\"If a customer wants to talk to a real person, they tap 'Talk to Human'. The bot mutes itself so it doesn't get in the way. On the right, a live chat opens for human support agents. When the customer sends a message, the bot stays quiet. The human agent replies from the dashboard, and it goes straight to WhatsApp.\""
        },
        {
            "step": "STEP 9: RESOLVING & UNMUTING THE BOT",
            "time_range": "3:40 - 3:55",
            "duration": "15s",
            "action": "Click button: <b>Unmute Bot / Resolve</b>.",
            "visual": "Operator Station closes. Session state turns back to green <b>ACTIVE_BOT</b>.",
            "voice": "\"When the agent is done helping, they click 'Unmute Bot'. The bot turns back on, ready to answer new questions automatically.\""
        },
        {
            "step": "STEP 10: PRODUCTION RIGOR & 103 AUTOMATED TESTS",
            "time_range": "3:55 - 4:10",
            "duration": "15s",
            "action": "Switch to terminal window and run: <b>uv run pytest</b>.",
            "visual": "All <b>103 automated tests pass green</b> in under 1.6 seconds.",
            "voice": "\"Finally, in the terminal, we can run our automated tests. All 103 tests pass in under two seconds, showing the code is clean and reliable. Thank you for watching!\""
        },
    ]

    for item in steps:
        header_text = f"<b>{item['step']}</b> &nbsp;&nbsp;&nbsp;&nbsp; <font color='#b45309'><b>[ ⏱️ {item['time_range']} | {item['duration']} ]</b></font>"
        card_content = [
            [Paragraph(header_text, step_title_style)],
            [Paragraph("<b>👉 ACTION:</b>", label_action)],
            [Paragraph(item["action"], text_action)],
            [Paragraph("<b>👀 ON SCREEN:</b>", label_visual)],
            [Paragraph(item["visual"], text_visual)],
            [Paragraph(f"<b>🎙️ SPOKEN SCRIPT (VOICEOVER: {item['time_range']}):</b>", label_voice)],
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
    story.append(Paragraph("Master Quick-Reference Cheat Sheet (4-Minute Pacing)", title_style))
    story.append(Spacer(1, 8))

    summary_table_data = [
        [
            Paragraph("Action (Click / Type)", th_style),
            Paragraph("⏱️ Time", th_style),
            Paragraph("What Happens on Screen", th_style),
            Paragraph("Voiceover Script (To Read Aloud)", th_style)
        ]
    ]

    for item in steps:
        summary_table_data.append([
            Paragraph(item["action"], td_action),
            Paragraph(f"<b>{item['time_range']}</b><br/>({item['duration']})", td_time),
            Paragraph(item["visual"], td_step),
            Paragraph(item["voice"], td_voice)
        ])

    st = Table(summary_table_data, colWidths=[105, 60, 140, 255])
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
