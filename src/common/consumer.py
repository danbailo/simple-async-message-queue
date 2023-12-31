from abc import ABCMeta, abstractmethod

import asyncio

from dataclasses import dataclass

from typing import Any

from common.requests import (
    async_post_fetch_and_lock,
    async_post_complete_record,
    async_get_unlock_record
)
from common.logger import logger

from .async_queue import AsyncQueueConsumer


@dataclass
class Consumer(metaclass=ABCMeta):
    batch_size: int

    @abstractmethod
    async def async_execute(self, item: dict[str, Any]):
        pass

    async def _async_handle_execute_record(self, item: dict[str, Any]):
        logger.info('processing record - id: %s', item["id"])
        try:
            return await self.async_execute(item["id"])
        except Exception:
            logger.error(
                'error when processing record - id: %s',
                item["id"], exc_info=True
            )
            response = await async_get_unlock_record(item['id'])
            logger.warning('record unlocked - item: %s', response)

    async def _async_process_record(self, item: dict[str, Any]):
        if not (result := await self._async_handle_execute_record(item)):
            return
        try:
            await async_post_complete_record(item['id'], result)
            logger.info('item completed with sucessfully - id: %s', item["id"])
            return result
        except Exception:
            logger.critical(
                'error when completing record - id: %s',
                item["id"], exc_info=True
            )
            response = await async_get_unlock_record(item['id'])
            logger.warning('record unlocked - item: %s', response)

    async def async_consume_batch(self):
        while True:
            result = []
            async for batch in async_post_fetch_and_lock(self.batch_size):
                logger.info('consuming %s items', len(batch))
                queue = AsyncQueueConsumer(
                    data_to_consume=batch,
                    action=self._async_process_record,
                    queue_size=len(batch)
                )
                for item in batch:
                    result += await queue.async_execute(item)
                break
            else:
                logger.info('nothing to fetch, sleeping 5 seconds...')
                await asyncio.sleep(5)

    async def async_consume_single(self):
        while True:
            async for item in async_post_fetch_and_lock(batch_size=1):
                logger.info('consuming 1 item')
                await self._async_handle_execute_record(item[0])
                break
            else:
                logger.info('nothing to fetch, sleeping 5 seconds...')
                await asyncio.sleep(5)
