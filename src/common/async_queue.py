import asyncio

from dataclasses import dataclass, field

from typing import Any, Coroutine

from .logger import logger


@dataclass
class AsyncQueueConsumer:
    action: Coroutine
    queue: asyncio.Queue = field(default=asyncio.Queue(200))

    def __post_init__(self):
        self.data_to_consume = []

    def __repr__(self) -> str:
        return f'AsyncQueueConsumer(<{self.data_to_consume}>)'

    async def _async_consume_queue(self):
        tasks = []
        while not self.queue.empty():
            item = await self.queue.get()
            tasks.append(asyncio.create_task(self.action(item)))
            self.queue.task_done()
        yield tasks

    async def add_item(self, item: Any):
        self.data_to_consume.append(item)

    async def execute(self):
        to_return = []
        for item in self.data_to_consume:
            await self.queue.put(item)
            if self.queue.full() or item is self.data_to_consume[-1]:
                async for tasks in self._async_consume_queue():
                    to_return += await asyncio.gather(
                        *tasks, return_exceptions=True
                    )
                logger.info(f'consumed {len(to_return)} items')
        return to_return
