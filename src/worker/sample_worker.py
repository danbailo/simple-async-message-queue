import asyncio

from dataclasses import dataclass

from typing import Any

from common.consumer import Consumer
from common.logger import logger

import random


@dataclass
class SampleWorker(Consumer):

    async def execute(self, item: dict[str, Any]):
        time_to_sleep = random.randint(1, 10)
        logger.info(f'time to execute item - {time_to_sleep}s')
        await asyncio.sleep(time_to_sleep)

        if random.choice([True, False]) is True:
            return {'result': 'processed with successfully!'}

        raise Exception('not lucky day, got error!')


if __name__ == '__main__':
    asyncio.run(SampleWorker().subscribe())
