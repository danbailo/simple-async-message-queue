import asyncio

from contextlib import asynccontextmanager

from typing import Annotated

from fastapi import FastAPI, File, UploadFile

from pandas import read_excel

from tortoise import Tortoise

from common.async_queue import AsyncQueueConsumer
from common.logger import logger
from common.requests import async_post_create_record

from .database.models import SampleIn, SampleOut, SampleModel

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Tortoise.init(
        db_url="postgres://postgres:postgres@localhost:7998/postgres",
        modules={'models': ['api.database.models']}
    )
    # TODO: maybe use migrations to generate schemas instead of lifespan.
    # just for develop
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()

app = FastAPI(lifespan=lifespan)


@app.post('/record', response_model=SampleOut)
async def create_record(body: SampleIn):
    sample_object = SampleModel(**body.model_dump())
    await sample_object.save()
    return sample_object


@app.get('/record', response_model=list[SampleOut])
async def get_records():
    return await SampleModel.all()


@app.post("/upload-files", status_code=204)
async def create_upload_file(
    files: Annotated[
        list[UploadFile],
        File(description="Excel file to submit data to database")
    ],
):
    result = []
    logger.info('files uploaded')
    for file in files:
        if file.content_type not in [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]:
            logger.warning(f'ignoring file - {file.filename}')
            continue
        logger.info(
            f'processing file - {file.filename}...'
        )
        tmp = []
        df = read_excel(file.file)
        data = df.to_dict(orient='records')
        consumer = AsyncQueueConsumer(
            data_to_consume=df.to_dict(orient='records'),
            action=async_post_create_record,
            queue=asyncio.Queue(400)
        )
        for item in data:
            tmp += await consumer.execute(item)
        result += tmp
        logger.info(
            f'file processed - {file.filename}, consumed {len(tmp)} items'
        )
    logger.info(f'application done - consumed {len(result)} items')
