import asyncio
import logging
from collections.abc import Awaitable, Callable

from gateway.models.domain import InboundMessageEvent

logger = logging.getLogger(__name__)
EventHandler = Callable[[InboundMessageEvent], Awaitable[None]]


class InProcessAsyncQueue:
    """In-memory asyncio queue worker pool for sub-30ms webhook acknowledgment."""

    def __init__(self, maxsize: int = 10000, num_workers: int = 2) -> None:
        self._queue: asyncio.Queue[InboundMessageEvent] = asyncio.Queue(maxsize=maxsize)
        self._num_workers = num_workers
        self._worker_tasks: list[asyncio.Task[None]] = []
        self._handler: EventHandler | None = None
        self._running = False

    def _ensure_workers_started(self) -> None:
        """Spawn worker tasks if they are not already running."""
        if self._worker_tasks or not self._running:
            return

        for worker_id in range(self._num_workers):
            task = asyncio.create_task(self._worker_loop(worker_id))
            self._worker_tasks.append(task)

    def start_worker(self, handler: EventHandler) -> None:
        """Register the message processor callback."""
        self._handler = handler
        self._running = True
        try:
            asyncio.get_running_loop()
            self._ensure_workers_started()
        except RuntimeError:
            # No running event loop yet; workers will start upon first enqueue
            pass

    async def enqueue(self, event: InboundMessageEvent) -> None:
        """Enqueue event non-blockingly and guarantee workers are active."""
        if self._running and not self._worker_tasks:
            self._ensure_workers_started()
        await self._queue.put(event)

    async def _worker_loop(self, worker_id: int) -> None:
        logger.debug("Starting queue worker %d", worker_id)
        while self._running:
            try:
                event = await self._queue.get()
                if self._handler:
                    try:
                        await self._handler(event)
                    except Exception:
                        logger.exception(
                            "Error processing event %s in worker %d",
                            event.wamid,
                            worker_id,
                        )
                self._queue.task_done()
            except asyncio.CancelledError:
                break

    async def stop(self) -> None:
        """Stop worker tasks and drain queue."""
        self._running = False
        for task in self._worker_tasks:
            task.cancel()
        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        self._worker_tasks.clear()
