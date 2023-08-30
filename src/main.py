import asyncio

from functools import wraps

import time

from pandas import read_excel

import typer

from common.logger import logger
from common.requests import async_post_create_record

from worker import WorkerEnum, InitWorker


app = typer.Typer()


@app.callback()
def callback():
    pass


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper


@app.command()
@coro
async def async_consume_batch(worker: WorkerEnum):
    worker = InitWorker(worker)
    await worker.async_consume_batch()


@app.command()
@coro
async def async_consume_single(worker: WorkerEnum):
    worker = InitWorker(worker)
    await worker.async_consume_single()


@app.command()
def insert_data_from_df(path: str = typer.Option()):
    df = read_excel(path)
    start = time.monotonic()
    for it, item in enumerate(df.to_dict(orient='records')):
        asyncio.run(async_post_create_record(item))
        logger.info(f'progress {it}/{len(df)}')
    end = time.monotonic()
    logger.info(f'time elapsed - {end - start:0.2f}s')


if __name__ == '__main__':
    app()
