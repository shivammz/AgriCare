# AgriCare/server/utils/httpx.py

import httpx

client: httpx.AsyncClient = None

def get_http_client() -> httpx.AsyncClient:
    global client
    if client is None:
        client = httpx.AsyncClient()
    return client

async def close_http_client():
    global client
    if client is not None:
        await client.aclose()
        client = None
