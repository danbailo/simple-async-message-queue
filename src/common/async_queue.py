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
    queue: asyncio.Queue = field(default=asyncio.Queue(200))

    async def _async_consume_queue(self):
        tasks = []
        while not self.queue.empty():
            item = await self.queue.get()
            tasks.append(asyncio.create_task(self.action(item)))
            self.queue.task_done()
        yield tasks

    async def _hash_item(self, value: Any):
        value_as_string = json.dumps(value, default=str).encode()
        return hashlib.md5(value_as_string, usedforsecurity=False).hexdigest()

    async def _check_if_is_last_element(self, item: Any):
        last_element = await self._hash_item(self.data_to_consume[-1])
        curr_element = await self._hash_item(item)
        return curr_element == last_element

    async def execute(self, item: Any):
        to_return = []
        await self.queue.put(item)
        if self.queue.full() or await self._check_if_is_last_element(item):
            async for tasks in self._async_consume_queue():
                to_return += await asyncio.gather(
                    *tasks, return_exceptions=True
                )
            logger.info(f'consumed {len(to_return)} items')
        return to_return
