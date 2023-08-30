import time

from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from pandas import read_excel

from common.async_queue import AsyncQueueConsumer
from common.logger import logger
from common.requests import async_post_create_record

router = APIRouter()


@router.post("/upload", status_code=204)
async def upload_file(
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
        start = time.monotonic()
        tmp = []
        df = read_excel(file.file)
        data = df.to_dict(orient='records')
        consumer = AsyncQueueConsumer(
            data_to_consume=data,
            action=async_post_create_record,
            queue_size=400
        )
        for item in data:
            tmp += await consumer.async_execute(item)
        logger.info(
            f'file processed - {file.filename}, consumed {len(tmp)} items'
        )
        result += tmp

    end = time.monotonic()
    logger.info(f'application done - consumed {len(result)} items')
    logger.info(f'time elapsed - {end - start:0.2f}s')
