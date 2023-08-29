from datetime import datetime

from tortoise.models import Model
from tortoise import fields

from pydantic import BaseModel


class TimestampMixin:
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)


class MyAbstractBaseModel(Model):
    id = fields.IntField(pk=True)

    class Meta:
        abstract = True


class SampleModel(TimestampMixin, MyAbstractBaseModel):
    number = fields.IntField()
    data = fields.TextField()
    processed = fields.BooleanField(default=False)
    locked = fields.BooleanField(default=False)
    result = fields.TextField(null=True)

    class Meta:
        table = 'sample'


class SampleIn(BaseModel):
    number: int
    data: str


class SampleOut(BaseModel):
    id: int
    number: int
    data: str
    result: str | None
    processed: bool
    locked: bool
    created_at: datetime
    modified_at: datetime
