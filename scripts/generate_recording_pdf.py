from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
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
        leftMargin=28,
        rightMargin=28,
        topMargin=28,
        bottomMargin=28,
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4,
    )
    
    sub_style = ParagraphStyle(
        "DocSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12,
    )

    checklist_style = ParagraphStyle(
        "Checklist",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
    )

    step_title_style = ParagraphStyle(
        "StepTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
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
        leading=12.5,
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
        fontSize=10.5,
        leading=14.5,
        textColor=colors.HexColor("#09090b"),
    )

    story = []

    # Title & Header
    story.append(Paragraph("WhatsApp Support Gateway - Video Demo Teleprompter", title_style))
    story.append(Paragraph("Dual-Pane Showcase: Sub-30ms Decoupling, Redis Streams, Anti-IDOR Security & Live WebSocket Takeover", sub_style))

    # Pre-Recording Checklist Box
    checklist_data = [
        [
            Paragraph("<b>PRE-RECORDING QUICK CHECKLIST:</b><br/>"
                      "1. Terminal: <code>uv run uvicorn gateway.main:app --reload --port 8000</code><br/>"
                      "2. Browser: Open <code>http://localhost:8000/demo</code> (100% zoom, both panes visible)<br/>"
                      "3. Screen Recorder: Press <b>Print Screen</b> key (or open Loom/OBS)", checklist_style)
        ]
    ]
    checklist_table = Table(checklist_data, colWidths=[556])
    checklist_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ecfdf5")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#10b981")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(checklist_table)
    story.append(Spacer(1, 14))

    steps = [
        {
            "step": "STEP 0: INTRO & ARCHITECTURE OVERVIEW",
            "action": "Hover mouse over WhatsApp phone on left, then over real-time metrics on right.",
            "visual": "Browser at <code>http://localhost:8000/demo</code> showing phone simulator and telemetry console.",
            "voice": "\"Hi there! Today I'm demonstrating an enterprise-grade WhatsApp Business API Support Gateway built with Python, FastAPI, and Meta Cloud API v20.<br/><br/>"
                     "Most WhatsApp chatbots fail in production because AI calls take over 3 seconds, triggering Meta's retry storm and spamming customers with duplicate messages. Here on the left is our WhatsApp phone simulator, and on the right is our real-time telemetry cockpit showing sub-30ms webhook decoupling, HMAC verification, distributed Redis Streams, and live human takeover.\""
        },
        {
            "step": "STEP 1: ORDER TRACKING (OWNER - SUB-30MS & READ RECEIPTS)",
            "action": "Click chip: <b>1. Track #ORD-1001</b>",
            "visual": "3 green typing dots appear ('typing...'), double grey ticks turn bright blue ('✓✓' read receipt), latency shows <20ms, bot replies with FedEx status and buttons.",
            "voice": "\"First, let's track an order. Notice the natural language processing: it recognized lowercase 'ord 1001' and mapped it instantly.<br/><br/>"
                     "Look at the telemetry: the webhook acknowledged the message in under 20 milliseconds, verified the HMAC-SHA256 signature, dispatched an official Meta 'mark_read' receipt turning the ticks blue, rendered realistic typing dots, and retrieved the order record with interactive action buttons.\""
        },
        {
            "step": "STEP 2: MULTI-TURN CONTEXT & RETURN POLICY ENFORCEMENT",
            "action": "Click chip: <b>2. Can I return it?</b>",
            "visual": "Bot resolves 'it' to #ORD-1001 and replies that in-transit orders cannot be returned until delivered.",
            "voice": "\"Next is multi-turn contextual memory and business policy enforcement. Notice I didn't re-type the order number; I simply asked 'Can I return it?'. The engine automatically resolved the pronoun 'it' to order #ORD-1001.<br/><br/>"
                     "Because the package is still in transit with FedEx, the agent strictly enforces return policy and explains that returns are only available once the item has been delivered.\""
        },
        {
            "step": "STEP 3: ANTI-IDOR SECURITY VERIFICATION CHALLENGE",
            "action": "Click chip: <b>3. Track #ORD-1002 (Security Check)</b>",
            "visual": "Bot intercepts query for #ORD-1002 (belongs to another phone), withholds shipment details, and asks for the last 4 digits on file.",
            "voice": "\"Now let's see our Anti-IDOR privacy protection. When a caller queries order #ORD-1002—which belongs to a different customer phone number—the gateway immediately blocks access.<br/><br/>"
                     "It withholds all private shipment information and issues a security challenge requiring the caller to verify the last 4 digits on file.\""
        },
        {
            "step": "STEP 4: OWNERSHIP AUTHENTICATION",
            "action": "Click chip: <b>4. Verify: 6543</b>",
            "visual": "Bot confirms 'Security Verification Successful!' and unlocks #ORD-1002 status ('PROCESSING').",
            "voice": "\"Once the customer enters the correct digits '6543', the security layer confirms ownership, unlocks the session, and presents the order status.\""
        },
        {
            "step": "STEP 5: DELIVERED ORDER RETURN REQUEST",
            "action": "Click chip: <b>5. Return #ORD-1003</b>",
            "visual": "Bot detects delivered order #ORD-1003 belongs to another phone (...2233) and requests 4-digit verification for return approval.",
            "voice": "\"Now let's request a return on a delivered order, #ORD-1003. Again, because it's associated with a separate account, the gateway demands verification before issuing prepaid postage.\""
        },
        {
            "step": "STEP 6: PROGRAMMATIC VECTOR PDF RETURN LABEL & BARCODE",
            "action": "Click chip: <b>6. Verify: 2233 (Get PDF)</b><br/>Then <b>click the PDF Document Card</b> in the phone.",
            "visual": "Bot verifies ownership, approves return, and sends document card: <code>📄 return_label_ORD-1003.pdf</code>. Clicking opens vector PDF in new tab with FedEx label, Code128 barcode & RMA packing slip.",
            "voice": "\"When I verify with '2233', the return is immediately approved.<br/><br/>"
                     "The gateway doesn't just send text—it programmatically generates a vector PDF shipping label using ReportLab. Clicking the document card opens the live label, complete with prepaid FedEx Ground routing, a scannable Code128 barcode encoding the RMA number, and an itemized warehouse packing slip.\""
        },
        {
            "step": "STEP 7: SHOPIFY ADMIN REST API ADAPTER",
            "action": "(Switch back to demo tab) Click chip: <b>7. Shopify #1001</b>",
            "visual": "Telemetry shows routing through <code>ShopifyOrderAdapter</code>. Bot returns live line items ('Classic Leather Jacket') and Shopify fulfillment status.",
            "voice": "\"The system is built on clean architectural ports and adapters. With a single environment variable, we can switch from our local database to a live Shopify Admin REST API. Here you see it parsing Shopify line items, fulfillment stages, and tracking numbers seamlessly.\""
        },
        {
            "step": "STEP 8: HUMAN ESCALATION & STRICT BOT MUTING",
            "action": "Click chip: <b>8. Talk to Human</b>",
            "visual": "Right pane: Session State switches to amber <b>ESCALATED_HUMAN</b>. Outbound webhook fires to n8n/Zendesk. Operator Card expands showing '🟢 Live WebSocket Connected'.",
            "voice": "\"Now for the most critical enterprise capability: Stateful Human Escalation and Live Operator Takeover.<br/><br/>"
                     "When the customer requests human help, an external webhook fires to Zendesk or n8n, and strict bot muting engages. Notice the session state is now ESCALATED_HUMAN, and our Operator Station has opened a real-time WebSocket bridge.\""
        },
        {
            "step": "STEP 9: BOT MUTING VERIFICATION (ZERO SPAM)",
            "action": "In phone chat input, type: <b>Where is my refund?</b> and click send.",
            "visual": "Message appears in WhatsApp feed. <b>Bot stays completely silent.</b> Customer message appears live inside Operator Chat Feed on right.",
            "voice": "\"Watch what happens when the customer types 'Where is my refund?': the bot stays completely silent so it never talks over human staff. Instead, the message was broadcast across the WebSocket and appeared directly in the operator console.\""
        },
        {
            "step": "STEP 10: REAL-TIME 2-WAY OPERATOR CHAT TAKEOVER",
            "action": "In Operator Desk input, type: <b>Hi, Agent Sarah here! Your refund of $189.50 has been released.</b> and click <b>Send as Agent</b>.",
            "visual": "Message appears immediately on customer phone with blue <code>👤 Agent Sarah (Live Support)</code> badge. Telemetry confirms outbound WhatsApp dispatch and transcript logging.",
            "voice": "\"As the human agent, I type: 'Hi, Agent Sarah here! Your refund has been released'.<br/><br/>"
                     "The moment I click Send, it dispatches over the WhatsApp channel, pops up immediately on the customer's phone, and is saved into the permanent customer transcript.\""
        },
        {
            "step": "STEP 11: SESSION RESOLUTION",
            "action": "Click button: <b>Unmute Bot / Resolve</b>",
            "visual": "Operator Station closes. Session State returns to green <b>ACTIVE_BOT</b>. Bot status resets to '● Online (Bot Active)'.",
            "voice": "\"Once the customer inquiry is resolved, clicking 'Unmute Bot' seamlessly re-activates automated bot handling for future inquiries.\""
        },
        {
            "step": "STEP 12: PRODUCTION RIGOR & 94-TEST SUITE",
            "action": "Switch to Terminal window and run: <b>uv run pytest</b>",
            "visual": "All <b>94 unit & integration tests pass green</b> in under 1.5 seconds.",
            "voice": "\"Under the hood, this is a fully tested production system. The application is containerized with Docker Compose and Redis Streams for horizontal worker scaling.<br/><br/>"
                     "The entire codebase features strict mypy typing, ruff linting, and 94 automated unit and integration tests passing in under 1.5 seconds.<br/><br/>"
                     "Thank you for watching, and I look forward to bringing this high-reliability architecture to your customer support operations!\""
        },
    ]

    for item in steps:
        card_content = [
            [Paragraph(f"<b>{item['step']}</b>", step_title_style)],
            [Paragraph("<b>ACTION (WHAT TO CLICK/TYPE):</b>", label_action)],
            [Paragraph(item["action"], text_action)],
            [Paragraph("<b>ON SCREEN (VISUAL REACTION):</b>", label_visual)],
            [Paragraph(item["visual"], text_visual)],
            [Paragraph("<b>SPOKEN SCRIPT (WHAT TO SAY):</b>", label_voice)],
            [Paragraph(item["voice"], text_voice)],
        ]
        t = Table(card_content, colWidths=[556])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
        ]))
        story.append(KeepTogether([t, Spacer(1, 10)]))

    doc.build(story)
    print(f"Generated PDF at: {PDF_PATH}")
    
    # Also write copy to static directory
    import shutil
    shutil.copy(PDF_PATH, STATIC_PATH)
    print(f"Copied PDF to: {STATIC_PATH}")

if __name__ == "__main__":
    build_pdf()
