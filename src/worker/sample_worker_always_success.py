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
        logger.info(f'time to execute item - {time_to_sleep}s')
        await asyncio.sleep(time_to_sleep)
        return {'result': 'processed with successfully!'}


if __name__ == '__main__':
    asyncio.run(SampleWorkerAlwaysSuccess().async_consume_single())
