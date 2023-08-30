import asyncio

from dataclasses import dataclass

from typing import Any

from common.consumer import Consumer
from common.logger import logger


@dataclass
class SampleWorkerAlwaysSuccess(Consumer):
    batch_size: int = 50

    async def async_execute(self, item: dict[str, Any]):
        time_to_sleep = 5
        logger.info('time to execute item - %ss', time_to_sleep)
        await asyncio.sleep(time_to_sleep)
        return {'result': 'processed with successfully!'}
