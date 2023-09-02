import pytest

from httpx import AsyncClient

from common.requests import async_post_create_record


@pytest.mark.anyio
async def test_create_record(client: AsyncClient):
    response = await client.post(
        '/record', json={'number': 1, 'data': 'test'}
    )
    assert response.status_code == 204


@pytest.mark.anyio
async def test_get_records(client: AsyncClient):
    response = await client.get('/record')
    assert response.status_code == 200
    data = response.json()[0]
    assert data['id'] == 1
    assert data['data'] == 'test'
    assert data['result'] is None
    assert data['processed'] is False
    assert data['locked'] is False


@pytest.mark.anyio
async def test_get_records_with_id(client: AsyncClient):
    response = await client.get('/record', params={'id': 1})
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.anyio
async def test_create_record_with_external_client(client: AsyncClient):
    response = await async_post_create_record(
        item={'number': 1, 'data': 'test'},
        client=client
    )
    assert response.status_code == 204


@pytest.mark.anyio
async def test_lock_record(client: AsyncClient):
    record_id = 1
    response = await client.get(f'/record/lock/{record_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == 1
    assert data['number'] == 1
    assert data['data'] == 'test'
    assert data['result'] is None
    assert data['processed'] is False
    assert data['locked'] is True


@pytest.mark.anyio
async def test_unlock_record(client: AsyncClient):
    record_id = 1
    response = await client.get(f'/record/unlock/{record_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == 1
    assert data['number'] == 1
    assert data['data'] == 'test'
    assert data['result'] is None
    assert data['processed'] is False
    assert data['locked'] is False


@pytest.mark.anyio
async def test_complete_record(client: AsyncClient):
    record_id = 1
    await client.get(f'/record/lock/{record_id}')
    response = await client.post(
        f'/record/complete/{record_id}', json={'result': 'foo'}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == 1
    assert data['number'] == 1
    assert data['data'] == 'test'
    assert data['result'] == 'foo'
    assert data['processed'] is True
    assert data['locked'] is True


@pytest.mark.anyio
async def test_error_when_complete_record(client: AsyncClient):
    record_id = 1
    await client.get(f'/record/unlock/{record_id}')
    response = await client.post(
        f'/record/complete/{record_id}', json={'result': 'foo'}
    )
    assert response.status_code == 500
    assert response.json()['detail'] == 'The record was not locked!'


@pytest.mark.anyio
async def test_fetch_and_lock(client: AsyncClient):
    response = await client.post(
        '/record/fetch-and-lock', json={'batch_size': 5}
    )
    assert response.status_code == 200
    for item in response.json():
        assert item['locked'] is True
