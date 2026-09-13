import asyncio
import sys
import time

from gateway.channel.mock import MockWhatsAppAdapter
from gateway.engine.processor import MessageProcessor
from gateway.models.domain import InboundMessageEvent, SessionStatus
from gateway.repository.order import InMemoryOrderRepository
from gateway.repository.session import InMemorySessionStore


async def run_cli_simulator() -> None:
    channel = MockWhatsAppAdapter()
    order_repo = InMemoryOrderRepository()
    session_store = InMemorySessionStore()

    processor = MessageProcessor(
        channel=channel,
        order_repo=order_repo,
        session_store=session_store,
    )

    phone = "15550192834"

    print("\n" + "=" * 64)
    print(" 📱  WHATSAPP SUPPORT GATEWAY — INTERACTIVE CLI SIMULATOR")
    print("=" * 64)
    print(f" Simulating WhatsApp user: {phone}")
    print(" Try typing: 'menu', '#ORD-1001', 'Return ORD-1003', or 'human'")
    print(" Type 'resolve' to simulate operator resolving escalation.")
    print(" Type 'exit' or Ctrl+C to quit.")
    print("=" * 64 + "\n")

    while True:
        try:
            user_input = input("\n👤 Customer: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting simulator. Goodbye!")
            sys.exit(0)

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Exiting simulator. Goodbye!")
            sys.exit(0)

        if user_input.lower() == "resolve":
            session_store.resolve_session(phone)
            print(" [Operator Station] ✅ Escalation resolved. Bot is unmuted for user.")
            continue

        channel.clear()
        wamid = f"wamid.CLI_{int(time.time() * 1000)}"

        event = InboundMessageEvent(
            wamid=wamid,
            sender_phone=phone,
            body=user_input,
            timestamp=str(int(time.time())),
        )

        start = time.perf_counter()
        await processor.process_event(event)
        latency_ms = (time.perf_counter() - start) * 1000

        session = session_store.get_session(phone)

        if channel.sent_messages:
            for msg in channel.sent_messages:
                print(f"\n🤖 WhatsApp Bot ({latency_ms:.1f}ms):")
                print(f" {msg.get('body')}")
                if "buttons" in msg:
                    print(" [Quick Replies]:")
                    for b in msg["buttons"]:
                        print(f"   🔘 [{b['id']}] {b['title']}")
        else:
            if session.status == SessionStatus.ESCALATED_HUMAN:
                print(
                    f"\n🤫 Bot is MUTED ({latency_ms:.1f}ms): Session is ESCALATED_HUMAN. "
                    "Inbound message was appended to transcript without auto-reply."
                )


def main() -> None:
    asyncio.run(run_cli_simulator())


if __name__ == "__main__":
    main()
