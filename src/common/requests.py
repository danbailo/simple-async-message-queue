from typing import Any

from httpx import AsyncClient

from common.env_var import get_env_var

BASE_API_URL = get_env_var('BASE_API_URL')


async def async_fetch(
    method: str,
    url: str,
    body: dict[str, Any] | None = None,
    files: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    cookies: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    return_as_json: bool = True,
    raise_for_status: bool = False,
    timeout: int = 120,
    client: AsyncClient | None = None
):
    if not files:
        files = {}
    if not cookies:
        cookies = {}
    if not headers:
        headers = {'Content-Type': 'application/json'}
    if not body:
        body = {}
    if not params:
        params = {}
    async with AsyncClient() as async_client:
        if client is None:
            client = async_client
        response = await client.request(
            method, url,
            json=body,
            params=params,
            files=files,
            headers=headers,
            timeout=timeout
        )
    if raise_for_status:
        response.raise_for_status()
    if return_as_json:
        return response.json()
    return response


async def async_post_create_record(
    item: dict[str, Any], **kwargs
):
    url = f'{BASE_API_URL}/record'
    return await async_fetch(
        'post', url, body=item, return_as_json=False, **kwargs
    )


async def async_post_upload_file(item: dict[str, Any], **kwargs):
    url = f'{BASE_API_URL}/file/upload'
    return await async_fetch(
        'post', url,
        files=item,
        headers={'accept': '*/*'},
        return_as_json=False,
        **kwargs
    )


async def async_post_fetch_and_lock(batch_size: int = 10, **kwargs):
    url = f'{BASE_API_URL}/record/fetch-and-lock'
    if (result := await async_fetch(
        'post', url, body={'batch_size': batch_size}, **kwargs
    )):
        yield result


async def async_post_complete_record(
    id_record: int,
    result: dict[str, Any],
    **kwargs
):
    url = f'{BASE_API_URL}/record/complete/{id_record}'
    return await async_fetch(
        'post', url,
        body=result,
        raise_for_status=True,
        **kwargs
    )


async def async_get_unlock_record(id_record: int, **kwargs):
    url = f'{BASE_API_URL}/record/unlock/{id_record}'
    return await async_fetch('get', url, **kwargs)
