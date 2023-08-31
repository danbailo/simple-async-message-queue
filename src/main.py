import asyncio

from pandas import read_excel

import typer

from common.decorators import coro, timeit
from common.logger import logger
from common.requests import async_post_create_record

from worker import WorkerEnum, InitWorker


app = typer.Typer()


@app.callback()
def callback():
    pass


@app.command()
@coro
async def async_consume_batch(worker: WorkerEnum):
    worker_obj = InitWorker(worker)
    await worker_obj.async_consume_batch()


@app.command()
@coro
async def async_consume_single(worker: WorkerEnum):
    worker_obj = InitWorker(worker)
    await worker_obj.async_consume_single()


@app.command()
@timeit
def insert_records_from_excel(path: str = typer.Option()):
    df = read_excel(path)
    for it, item in enumerate(df.to_dict(orient='records'), start=1):
        asyncio.run(async_post_create_record(item))
        logger.info('progress %s/%s', it, len(df))


if __name__ == '__main__':
    app()
