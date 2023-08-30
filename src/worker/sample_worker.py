import asyncio

from dataclasses import dataclass

from typing import Any

from common.consumer import Consumer
from common.logger import logger

import random


@dataclass
class SampleWorker(Consumer):
    batch_size: int = 10

    async def async_execute(self, item: dict[str, Any]):
        time_to_sleep = random.randint(1, 10)
        logger.info('time to execute item - %ss', time_to_sleep)
        await asyncio.sleep(time_to_sleep)

        if random.choice([True, False]) is True:
            return {'result': 'processed with successfully!'}

        raise Exception('not lucky day, got error!')
