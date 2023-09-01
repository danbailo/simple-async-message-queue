import asyncio

from dataclasses import dataclass, field

import hashlib

import json

from typing import Any, Coroutine

from .logger import logger


@dataclass
class AsyncQueueConsumer:
    data_to_consume: list[Any]
    action: Coroutine
    queue_size: int
    action_kwargs: dict[str, Any] = field(default_factory=lambda: {})

    _queue: asyncio.Queue = field(default=None, init=False)

    @property
    def queue(self):
        return self._queue

    @queue.setter
    def queue(self, value):
        if not self._queue and isinstance(value, asyncio.Queue):
            self._queue = value

    def __post_init__(self):
        self._queue = asyncio.Queue(self.queue_size)

    async def _async_consume_queue(self):
        tasks = []
        while not self.queue.empty():
            item = await self.queue.get()
            tasks.append(asyncio.create_task(
                self.action(item=item, **self.action_kwargs)
            ))
            self.queue.task_done()
        yield tasks

    async def _async_hash_item(self, value: Any):
        value_as_string = json.dumps(value, default=str).encode()
        return hashlib.md5(value_as_string, usedforsecurity=False).hexdigest()

    async def _async_check_if_is_last_element(self, item: Any):
        last_element = await self._async_hash_item(self.data_to_consume[-1])
        curr_element = await self._async_hash_item(item)
        return curr_element == last_element

    async def async_execute(self, item: Any):
        to_return = []
        await self.queue.put(item)
        is_last_element = await self._async_check_if_is_last_element(item)
        if self.queue.full() or is_last_element is True:
            async for tasks in self._async_consume_queue():
                to_return += await asyncio.gather(
                    *tasks, return_exceptions=True
                )
            logger.info('consumed %s items', len(to_return))
        return to_return
