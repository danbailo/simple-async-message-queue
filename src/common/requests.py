from typing import Any

from httpx import AsyncClient


async def async_fetch(
    method: str,
    url: str,
    body: dict[str, Any],
    cookies: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    raise_for_status: bool = False,
    timeout: int = 120
):
    if not cookies:
        cookies = {}
    if not headers:
        headers = {'Content-Type': 'application/json'}
    async with AsyncClient() as client:
        response = await client.request(
            method, url, json=body, headers=headers, timeout=timeout
        )
    if raise_for_status:
        response.raise_for_status()
    return response.json()


async def async_post_create_record(item: dict[str, Any]):
    return await async_fetch(
        'post', 'http://localhost:8000/record', body=item
    )