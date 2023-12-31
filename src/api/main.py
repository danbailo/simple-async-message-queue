from contextlib import asynccontextmanager

from fastapi import FastAPI

from tortoise import Tortoise

from common.env_var import get_env_var

from .routers import file, record

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Tortoise.init(
        db_url=get_env_var('DATABASE_CONN_STRING'),
        modules={'models': ['api.database.models']}
    )
    # TODO: maybe use migrations to generate schemas instead of lifespan.
    # just for develop
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()

app = FastAPI(lifespan=lifespan)

app.include_router(
    file.router,
    prefix='/file',
    tags=['files']
)

app.include_router(
    record.router,
    prefix='/record',
    tags=['records']
)
