
import pytest

from httpx import AsyncClient
from common.requests import async_post_upload_file


@pytest.mark.anyio
async def test_upload_file(client: AsyncClient):
    files = {
        'files': (
            'sample.xlsx',
            open('../resources/sample.xlsx', 'rb'),
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    }
    response = await client.post(
        '/file/upload',
        files=files,
        headers={'accept': '*/*'}
    )
    assert response.status_code == 204


@pytest.mark.anyio
async def test_upload_file_with_external_client(client: AsyncClient):
    files = {
        'files': (
            'sample.xlsx',
            open('../resources/sample.xlsx', 'rb'),
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    }
    response = await async_post_upload_file(files, client=client)
    assert response.status_code == 204
