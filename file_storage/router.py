from file_storage.typings import AioHttpApplication
from file_storage.views import FileStorageHandler


def setup_api_routes(app: AioHttpApplication) -> None:
    """Setup landing API routes."""
    app.router.add_put("/api/v1/file_storage", FileStorageHandler.put)
    app.router.add_get(r"/api/v1/file_storage/{uuid}", FileStorageHandler.get)
