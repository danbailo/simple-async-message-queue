import random

from fastapi import APIRouter, HTTPException

from tortoise.queryset import QuerySet

from api.database.models import SampleIn, SampleOut, SampleModel

from .base_router import CommonQuery

router = APIRouter()


@router.get('/fetch-and-lock', response_model=SampleOut | None)
async def fetch_and_lock():
    if not (result := await SampleModel.filter(
        processed=False, locked=False
    )):
        return
    result = random.choice(result)
    result.locked = True
    await result.save()
    return result


@router.get('/lock/{id}', response_model=SampleOut)
async def lock_record(id: int):
    result = await SampleModel.get(id=id)
    result.locked = True
    await result.save()
    return result


@router.get('/unlock/{id}', response_model=SampleOut)
async def unlock_record(id: int):
    result = await SampleModel.get(id=id)
    result.locked = False
    await result.save()
    return result


@router.get('/complete/{id}', response_model=SampleOut)
async def complete_record(id: int):
    result = await SampleModel.get(id=id)
    if not result.locked:
        raise HTTPException(500, 'The record was not locked!')
    result.processed = True
    await result.save()
    return result


@router.post('', response_model=SampleOut)
async def create_record(body: SampleIn):
    sample_object = SampleModel(**body.model_dump())
    await sample_object.save()
    return sample_object


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
