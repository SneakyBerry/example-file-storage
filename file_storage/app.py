import typing as tp

from aiohttp import web
from file_storage.router import setup_api_routes
from file_storage.setup import on_shutdown, on_startup
from file_storage.typings import AioHttpApplication


def get_application() -> AioHttpApplication:
    """Get app."""
    app: AioHttpApplication = tp.cast(AioHttpApplication, web.Application())
    setup_api_routes(app)
    app.on_startup.extend(on_startup)
    app.on_shutdown.extend(on_shutdown)
    return app
