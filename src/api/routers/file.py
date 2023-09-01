from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from pandas import read_excel

from common.async_queue import AsyncQueueConsumer
from common.logger import logger
from common.requests import async_post_create_record
from common.decorators import async_timeit

router = APIRouter()


@router.post("/upload", status_code=204)
@async_timeit
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
            logger.warning('ignoring file - %s', file.filename)
            continue
        logger.info('processing file - %s...', file.filename)
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
            'file processed - %s, consumed %s items', file.filename, len(tmp)
        )
        result += tmp
    logger.info('application done - consumed %s items', len(result))
