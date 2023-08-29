import asyncio

import time

from pandas import read_excel

import typer

from common.logger import logger
from common.requests import async_post_create_record

app = typer.Typer()


@app.callback()
def callback():
    pass


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
