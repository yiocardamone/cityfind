from aiohttp import web


async def healthcheck(_request: web.Request) -> web.Response:
    return web.Response(text="OK")
