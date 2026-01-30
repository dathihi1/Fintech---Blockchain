"""
Trade Queue Service
Async queue for processing trades in the background.
Replaces Kafka for simpler, in-memory processing.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
import uuid
import structlog

logger = structlog.get_logger()


@dataclass
class QueueMessage:
    """Message in the queue"""
    id: str
    type: str  # 'trade_created', 'trade_closed', 'analyze_request'
    payload: Dict[str, Any]
    created_at: datetime
    retry_count: int = 0
    max_retries: int = 3


class TradeQueue:
    """
    Async queue for processing trades in the background.
    Replaces Kafka for simpler, in-memory processing.

    Features:
    - Multiple workers for parallel processing
    - Handler registration for different message types
    - Automatic retry on failure
    - Graceful shutdown
    """

    def __init__(self, max_size: int = 1000):
        self._queue: asyncio.Queue[QueueMessage] = asyncio.Queue(maxsize=max_size)
        self._handlers: Dict[str, List[Callable]] = {}
        self._running = False
        self._workers: List[asyncio.Task] = []
        self._processed_count = 0
        self._error_count = 0

    def register_handler(self, message_type: str, handler: Callable):
        """
        Register a handler for a message type.

        Args:
            message_type: Type of message to handle (e.g., 'trade_created')
            handler: Async or sync function to handle the message
        """
        if message_type not in self._handlers:
            self._handlers[message_type] = []
        self._handlers[message_type].append(handler)
        logger.info("Handler registered", message_type=message_type, handler=handler.__name__)

    async def publish(self, message_type: str, payload: Dict[str, Any]) -> str:
        """
        Publish a message to the queue.

        Args:
            message_type: Type of message
            payload: Message data

        Returns:
            Message ID
        """
        message = QueueMessage(
            id=str(uuid.uuid4()),
            type=message_type,
            payload=payload,
            created_at=datetime.utcnow()
        )

        try:
            await asyncio.wait_for(
                self._queue.put(message),
                timeout=5.0
            )
            logger.debug("Message published", message_id=message.id, type=message_type)
            return message.id
        except asyncio.TimeoutError:
            logger.error("Queue full, message dropped", message_type=message_type)
            raise RuntimeError("Queue is full")

    async def _process_message(self, message: QueueMessage) -> bool:
        """
        Process a single message with all registered handlers.

        Args:
            message: Message to process

        Returns:
            True if processed successfully, False otherwise
        """
        handlers = self._handlers.get(message.type, [])

        if not handlers:
            logger.warning("No handlers for message type", type=message.type)
            return True

        success = True
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message.payload)
                else:
                    handler(message.payload)
            except Exception as e:
                logger.error(
                    "Handler error",
                    message_id=message.id,
                    handler=handler.__name__,
                    error=str(e)
                )
                success = False

        return success

    async def _worker(self, worker_id: int):
        """
        Worker task to process messages from the queue.

        Args:
            worker_id: Worker identifier for logging
        """
        logger.info("Queue worker started", worker_id=worker_id)

        while self._running:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=1.0
                )

                # Process message
                success = await self._process_message(message)

                if success:
                    self._processed_count += 1
                else:
                    self._error_count += 1
                    # Retry if not exceeded max retries
                    if message.retry_count < message.max_retries:
                        message.retry_count += 1
                        await self._queue.put(message)
                        logger.info(
                            "Message requeued for retry",
                            message_id=message.id,
                            retry_count=message.retry_count
                        )

                self._queue.task_done()

            except asyncio.TimeoutError:
                # No message available, continue loop
                continue
            except Exception as e:
                logger.error("Worker error", worker_id=worker_id, error=str(e))

        logger.info("Queue worker stopped", worker_id=worker_id)

    async def start(self, num_workers: int = 3):
        """
        Start the queue with worker tasks.

        Args:
            num_workers: Number of worker tasks to spawn
        """
        if self._running:
            logger.warning("Queue already running")
            return

        self._running = True
        self._workers = [
            asyncio.create_task(self._worker(i))
            for i in range(num_workers)
        ]
        logger.info("Trade queue started", workers=num_workers)

    async def stop(self):
        """Stop the queue and wait for workers to finish."""
        if not self._running:
            return

        self._running = False

        # Wait for queue to be empty
        try:
            await asyncio.wait_for(self._queue.join(), timeout=10.0)
        except asyncio.TimeoutError:
            logger.warning("Queue not empty on shutdown, some messages may be lost")

        # Cancel workers
        for worker in self._workers:
            worker.cancel()

        # Wait for workers to finish
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)

        logger.info(
            "Trade queue stopped",
            processed=self._processed_count,
            errors=self._error_count
        )

    @property
    def pending_count(self) -> int:
        """Get number of pending messages in queue"""
        return self._queue.qsize()

    @property
    def stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "running": self._running,
            "pending": self.pending_count,
            "processed": self._processed_count,
            "errors": self._error_count,
            "workers": len(self._workers)
        }


# Singleton instance
_trade_queue: Optional[TradeQueue] = None


def get_trade_queue() -> TradeQueue:
    """Get or create the trade queue singleton"""
    global _trade_queue
    if _trade_queue is None:
        _trade_queue = TradeQueue()
    return _trade_queue
