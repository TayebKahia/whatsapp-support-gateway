"""Outbound event dispatcher for external automation webhooks (n8n, Make, Zapier)."""

from gateway.events.dispatcher import OutboundEventDispatcher

__all__ = ["OutboundEventDispatcher"]
