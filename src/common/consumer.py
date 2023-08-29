from abc import ABCMeta, abstractmethod

import asyncio

from dataclasses import dataclass

from typing import Any

from common.requests import (
    async_get_fetch_and_lock,
    async_post_complete_record,
    async_get_unlock_record
)
from common.logger import logger


@dataclass
class Consumer(metaclass=ABCMeta):

    async def _process_record(self, item: dict[str, Any]):
        logger.info(f'processing record - id: {item["id"]}')
        try:
            result = await self.execute(item["id"])
        except Exception:
            logger.error(
                f'error when processing record - id: {item["id"]}',
                exc_info=True
            )
            return
        return result

    @abstractmethod
    async def execute(self):
        pass

    async def subscribe(self):
        while True:
            async for item in async_get_fetch_and_lock():
                if not (result := await self._process_record(item)):
                    response = await async_get_unlock_record(item['id'])
                    logger.warning(f'record unlocked - item: {response}')
                    break

                try:
                    await async_post_complete_record(item['id'], result)
                    logger.info('item completed with sucessfully!')
                except Exception:
                    logger.critical(
                        f'error when completing record - id: {item["id"]}',
                        exc_info=True
                    )
                    response = await async_get_unlock_record(item['id'])
                    logger.warning(f'record unlocked - item: {response}')
                finally:
                    break
            else:
                logger.info('nothing to fetch, sleeping 5 seconds...')
                await asyncio.sleep(5)
