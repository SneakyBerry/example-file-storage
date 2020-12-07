from aiohttp import web
from asyncpg.pool import Pool


class AioHttpApplication(web.Application):
    """Type hints for application with additional attributes."""

    db: Pool
