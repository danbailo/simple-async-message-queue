import asyncio

from typing import Any

from httpx import AsyncClient


async def async_fetch(
    method: str,
    url: str,
    body: dict[str, Any] | None = None,
    cookies: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    raise_for_status: bool = False,
    timeout: int = 120
):
    if not cookies:
        cookies = {}
    if not headers:
        headers = {'Content-Type': 'application/json'}
    if not body:
        body = {}
    async with AsyncClient() as client:
        response = await client.request(
            method, url, json=body, headers=headers, timeout=timeout
        )
    if raise_for_status:
        response.raise_for_status()
    return response.json()


async def async_post_create_record(item: dict[str, Any]):
    await asyncio.sleep(3)
    url = 'http://localhost:8000/record'
    return await async_fetch(
        'post', url, body=item
    )


async def async_get_fetch_and_lock():
    url = 'http://localhost:8000/record/fetch-and-lock'
    if (result := await async_fetch('get', url)):
        yield result
