import asyncio

from dataclasses import dataclass

from common.requests import async_get_fetch_and_lock
from common.logger import logger


@dataclass
class SampleWorker:

    async def subscribe(self):
        while True:
            async for item in async_get_fetch_and_lock():
                logger.info('processing item...')
                await asyncio.sleep(5)
                break
            else:
                logger.info('nothing to fetch, sleeping 5 seconds...')
                await asyncio.sleep(5)


if __name__ == '__main__':
    asyncio.run(SampleWorker().subscribe())
