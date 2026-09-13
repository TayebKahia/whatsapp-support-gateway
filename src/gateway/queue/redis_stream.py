import asyncio
import logging
from typing import Any

import redis.asyncio as aioredis
from redis.exceptions import ResponseError

from gateway.models.domain import InboundMessageEvent
from gateway.queue.base import EventHandler, QueuePort

logger = logging.getLogger(__name__)


class RedisStreamQueue(QueuePort):
    """Distributed message queue backed by Redis Streams and Consumer Groups.

    Provides horizontal scalability across multiple gateway container instances,
    at-least-once message delivery via XREADGROUP, and explicit acknowledgments via XACK.
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        stream_key: str = "whatsapp:events",
        consumer_group: str = "gateway_workers",
        consumer_name: str = "worker-1",
        redis_client: Any | None = None,
        poll_interval_ms: int = 1000,
    ) -> None:
        self.redis_url = redis_url
        self.stream_key = stream_key
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name
        self._client = redis_client
        self._owns_client = redis_client is None
        self._poll_interval_ms = poll_interval_ms
        self._handler: EventHandler | None = None
        self._worker_task: asyncio.Task[None] | None = None
        self._running = False

    async def _get_client(self) -> Any:
        if self._client is None:
            self._client = aioredis.from_url(self.redis_url, decode_responses=True)
        return self._client

    async def enqueue(self, event: InboundMessageEvent) -> None:
        """Enqueue an inbound event to the Redis Stream via XADD."""
        client = await self._get_client()
        payload = event.model_dump_json()
        await client.xadd(self.stream_key, {"payload": payload})
        logger.debug("Enqueued message %s to Redis stream %s", event.wamid, self.stream_key)

    def start_worker(self, handler: EventHandler) -> None:
        """Register processor callback and spawn the consumer group loop."""
        self._handler = handler
        self._running = True
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                self._worker_task = asyncio.create_task(self._worker_loop())
        except RuntimeError:
            # No running loop yet; worker will be spawned on first async call or lifecycle
            pass

    async def _ensure_worker_task(self) -> None:
        if self._running and (self._worker_task is None or self._worker_task.done()):
            self._worker_task = asyncio.create_task(self._worker_loop())

    async def _init_consumer_group(self, client: Any) -> None:
        """Ensure consumer group exists on the stream (MKSTREAM=True)."""
        try:
            await client.xgroup_create(
                self.stream_key,
                self.consumer_group,
                id="0",
                mkstream=True,
            )
            logger.info(
                "Created Redis consumer group '%s' on stream '%s'",
                self.consumer_group,
                self.stream_key,
            )
        except ResponseError as exc:
            # BUSYGROUP means the group was already initialized by another worker
            if "BUSYGROUP" in str(exc):
                logger.debug("Consumer group '%s' already exists", self.consumer_group)
            else:
                logger.warning("Error creating consumer group: %s", exc)

    async def _worker_loop(self) -> None:
        client = await self._get_client()
        await self._init_consumer_group(client)

        logger.info(
            "Redis worker '%s' listening on group '%s' (stream '%s')",
            self.consumer_name,
            self.consumer_group,
            self.stream_key,
        )

        while self._running:
            try:
                # Read new unacknowledged messages assigned to this consumer
                entries = await client.xreadgroup(
                    groupname=self.consumer_group,
                    consumername=self.consumer_name,
                    streams={self.stream_key: ">"},
                    count=10,
                    block=self._poll_interval_ms,
                )
                if not entries:
                    continue

                for _stream, messages in entries:
                    for msg_id, fields in messages:
                        raw_payload = fields.get("payload")
                        if isinstance(raw_payload, bytes):
                            raw_payload = raw_payload.decode("utf-8")

                        if raw_payload and self._handler:
                            try:
                                event = InboundMessageEvent.model_validate_json(raw_payload)
                                await self._handler(event)
                                await client.xack(self.stream_key, self.consumer_group, msg_id)
                            except Exception:
                                logger.exception(
                                    "Error processing Redis stream message %s",
                                    msg_id,
                                )
            except asyncio.CancelledError:
                break
            except Exception:
                if not self._running:
                    break
                logger.exception("Unexpected error in Redis stream consumer loop")
                await asyncio.sleep(0.5)

    async def stop(self) -> None:
        """Drain worker task and close Redis connections."""
        self._running = False
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        self._worker_task = None

        if self._owns_client and self._client is not None:
            if hasattr(self._client, "aclose"):
                await self._client.aclose()
            elif hasattr(self._client, "close"):
                res = self._client.close()
                if asyncio.iscoroutine(res):
                    await res
            self._client = None
