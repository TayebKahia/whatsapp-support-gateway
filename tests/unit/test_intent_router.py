from gateway.engine.router import Intent, IntentRouter


def test_intent_router_menu_keywords() -> None:
    router = IntentRouter()
    assert router.route("menu") == Intent.MENU
    assert router.route("Help please") == Intent.MENU
    assert router.route("Options") == Intent.MENU


def test_intent_router_escalation_keywords() -> None:
    router = IntentRouter()
    assert router.route("I want to speak to a human") == Intent.HUMAN_ESCALATION
    assert router.route("agent") == Intent.HUMAN_ESCALATION
    assert router.route("Can I talk to a live representative?") == Intent.HUMAN_ESCALATION
    assert router.route("Let me speak to a manager") == Intent.HUMAN_ESCALATION


def test_intent_router_order_query_keywords() -> None:
    router = IntentRouter()
    assert router.route("Where is my order ORD-1001?") == Intent.ORDER_QUERY
    assert router.route("Track my package") == Intent.ORDER_QUERY
    assert router.route("When will #ORD-1002 arrive?") == Intent.ORDER_QUERY
    assert router.route("where is ord 1001") == Intent.ORDER_QUERY
    assert router.route("status for #1001") == Intent.ORDER_QUERY


def test_intent_router_return_keywords() -> None:
    router = IntentRouter()
    assert router.route("I want to return an item") == Intent.RETURN_QUERY
    assert router.route("How do I request a refund?") == Intent.RETURN_QUERY


def test_intent_router_interactive_button_id() -> None:
    router = IntentRouter()
    assert router.route("Button Click", interactive_id="btn_menu") == Intent.MENU
    assert router.route("Button Click", interactive_id="btn_human") == Intent.HUMAN_ESCALATION
    assert router.route("Button Click", interactive_id="btn_track") == Intent.ORDER_QUERY
    assert router.route("Button Click", interactive_id="btn_return") == Intent.RETURN_QUERY
