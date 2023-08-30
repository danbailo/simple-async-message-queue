import asyncio

from typing import Any

from httpx import AsyncClient


async def async_fetch(
    method: str,
    url: str,
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    cookies: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    return_as_json: bool = True,
    raise_for_status: bool = False,
    timeout: int = 120
):
    if not cookies:
        cookies = {}
    if not headers:
        headers = {'Content-Type': 'application/json'}
    if not body:
        body = {}
    if not params:
        params = {}
    async with AsyncClient() as client:
        response = await client.request(
            method, url,
            json=body,
            params=params,
            headers=headers,
            timeout=timeout
        )
    if raise_for_status:
        response.raise_for_status()
    if return_as_json is True:
        return response.json()
    return response


async def async_post_create_record(item: dict[str, Any]):
    url = 'http://localhost:8000/record'
    await asyncio.sleep(3)
    return await async_fetch('post', url, body=item, return_as_json=False)


async def async_post_fetch_and_lock(batch_size: int = 10):
    url = 'http://localhost:8000/record/fetch-and-lock'
    if (result := await async_fetch(
        'post', url, body={'batch_size': batch_size}
    )):
        yield result


async def async_post_complete_record(id_record: int, result: dict[str, Any]):
    url = f'http://localhost:8000/record/complete/{id_record}'
    return await async_fetch(
        'post', url,
        body=result,
        raise_for_status=True
    )


async def async_get_unlock_record(id_record: int):
    url = f'http://localhost:8000/record/unlock/{id_record}'
    return await async_fetch('get', url)
