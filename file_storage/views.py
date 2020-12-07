import logging
from typing import cast
from uuid import uuid4

from aiohttp import web
from asyncpg import Connection
from file_storage.sql import (
    insert_meta_query,
    retrieve_data_by_uuid,
    upload_data_query,
)
from file_storage.typings import AioHttpApplication
from pydantic import UUID4


class FileStorageHandler:
    logger = logging.getLogger("FileStorageHandler")

    @classmethod
    async def put(cls, request: web.Request):
        """Upload action handler."""
        app: AioHttpApplication = cast(AioHttpApplication, request.app)
        insert_data_query = upload_data_query()
        payload = await request.read()
        conn: Connection
        async with app.db.acquire() as conn:
            async with conn.transaction():
                uploaded_file = await conn.fetchrow(insert_data_query, payload)
                file_hash = uploaded_file["hash"]
                file_uuid = str(uuid4())
                cls.logger.info(
                    f"File hash: {file_hash}, file_uuid: {file_uuid}"
                )
                await conn.execute(
                    insert_meta_query(),
                    file_uuid,
                    request.content_type,
                    file_hash,
                )
                return web.json_response(
                    {"link": str(request.rel_url / file_uuid)},
                    status=web.HTTPCreated.status_code,
                )

    @classmethod
    async def get(cls, request: web.Request):
        """Get file from storage by UUID."""
        try:
            uuid = UUID4(request.match_info["uuid"])
        except ValueError:
            raise web.HTTPBadRequest
        app: AioHttpApplication = cast(AioHttpApplication, request.app)
        conn: Connection
        query = retrieve_data_by_uuid()
        async with app.db.acquire() as conn:
            data = await conn.fetchrow(query, uuid)
            if not data:
                raise web.HTTPNotFound
            return web.Response(
                body=data["data"], content_type=data["content_type"]
            )
