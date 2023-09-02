from httpx import AsyncClient

import pytest

from tortoise import Tortoise

from common.logger import logger

from ..main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        logger.debug('client ready')
        yield client


@pytest.fixture(scope="session", autouse=True)
async def lifespan():
    await Tortoise.init(
        # db_url=get_env_var('DATABASE_CONN_STRING'),
        db_url='sqlite://:memory:',
        modules={'models': ['api.database.models']}
    )
    logger.debug('connected on db')

    await Tortoise.generate_schemas()
    logger.debug('generated schemas')

    yield
    await Tortoise._drop_databases()
    await Tortoise.close_connections()
    logger.debug('dropping/closing db')
