import asyncpg
from file_storage.conf import settings
from file_storage.typings import AioHttpApplication


async def get_db() -> asyncpg.pool.Pool:
    """
    Creates postgres pool.

    We need separate function for testing purposes.
    """
    return await asyncpg.create_pool(
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_SERVER,
        port=settings.DB_PORT,
        statement_cache_size=0,
    )


async def setup_app_postgres(app: AioHttpApplication) -> None:
    """Creates postgres pool for app."""
    app.db = await get_db()


async def shutdown_postgres(app: AioHttpApplication):
    """Close postgres."""
    await app.db.close()


on_startup = (setup_app_postgres,)
on_shutdown = (shutdown_postgres,)
