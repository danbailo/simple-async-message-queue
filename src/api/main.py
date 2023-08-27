import asyncio

from contextlib import asynccontextmanager

from typing import Annotated

from fastapi import FastAPI, File, UploadFile

from pandas import read_excel

from common.async_queue import AsyncQueueConsumer
from common.logger import logger

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # before
    yield
    # after

app = FastAPI(lifespan=lifespan)


@app.get('/')
async def hello_world():
    return {'detail': 'hello-world'}


async def foo(item):
    return str(item)


@app.post("/uploadfiles")
async def create_upload_file(
    files: Annotated[
        list[UploadFile], File(description="A file read as UploadFile")
    ],
):
    result = []
    for item in files:
        if item.content_type not in [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]:
            logger.info(f'ignoring file - {item.filename}')
            continue
        tmp = []
        df = read_excel(item.file)
        consumer = AsyncQueueConsumer(
            data_to_consume=df.values.tolist(),
            action=foo,
            queue=asyncio.Queue(200)
        )
        for row in df.iterrows():
            _, data = row
            tmp += await consumer.execute(data.tolist())
        result += tmp
        logger.info(
            f'file processed - {item.filename}, consumed {len(tmp)} items'
        )
    logger.info(f'application done - consumed {len(result)} items')
    return result
