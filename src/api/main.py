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
    for item in files:
        if item.content_type not in [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]:
            logger.info(f'ignoring file - {item.filename}')
            continue
        df = read_excel(item.file)
        consumer = AsyncQueueConsumer(
            foo, asyncio.Queue(200)
        )
        for row in df.iterrows():
            _, data = row
            await consumer.add_item(data)
    return await consumer.execute()
