from fastapi import APIRouter, HTTPException

from pydantic import BaseModel

from tortoise.queryset import QuerySet

from api.database.models import SampleIn, SampleOut, SampleModel

from .base import CommonQuery

router = APIRouter()


class CompleteRecordBody(BaseModel):
    result: str


class FetchAndLockRecordBody(BaseModel):
    batch_size: int


@router.post('/fetch-and-lock', response_model=list[SampleOut])
async def fetch_and_lock(body: FetchAndLockRecordBody):
    if not (
        result := await SampleModel
        .filter(processed=False, locked=False)
        .order_by('created_at')
        .limit(body.batch_size)
        .select_for_update(skip_locked=True)
    ):
        return []
    for item in result:
        item.locked = True
    await SampleModel.bulk_update(result, fields=['locked'])
    return result


@router.get('/lock/{id}', response_model=SampleOut)
async def lock_record(id: int):
    item = await SampleModel.get(id=id)
    item.locked = True
    await item.save()
    return item


@router.get('/unlock/{id}', response_model=SampleOut)
async def unlock_record(id: int):
    item = await SampleModel.get(id=id)
    item.locked = False
    await item.save()
    return item


@router.post('/complete/{id}', response_model=SampleOut)
async def complete_record(id: int, body: CompleteRecordBody):
    item = await SampleModel.get(id=id)
    if not item.locked:
        raise HTTPException(500, 'The record was not locked!')
    item.processed = True
    item.result = body.result
    await item.save()
    return item


@router.post('', status_code=204)
async def create_record(body: SampleIn):
    sample_object = SampleModel(**body.model_dump())
    await sample_object.save()


@router.get('', response_model=list[SampleOut])
async def get_records(
    query: CommonQuery,
    id: str = None,
    processed: bool = None,
    locked: bool = None,
):
    params = {
        'id': id,
        'processed': processed,
        'locked': locked,
    }
    params = {key: value for key, value in params.items() if value is not None}
    query = QuerySet(SampleModel).filter(
        **params
    ).offset(query.offset).limit(query.limit)
    return await query.all()
