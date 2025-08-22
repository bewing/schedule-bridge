from typing import Any
import httpx


class HTTPXClientWrapper:
    async_client = None | httpx.AsyncClient
    args = list
    kwargs = dict[str, Any]

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def start(self):
        self.async_client = httpx.AsyncClient(*self.args, **self.kwargs)

    async def stop(self):
        assert isinstance(self.async_client, httpx.AsyncClient)
        await self.async_client.aclose()

    def __call__(self):
        assert self.async_client is not None
        return self.async_client
