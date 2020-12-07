import asyncio
from uuid import uuid4

from aiohttp import web


async def test_get_invalid_uuid(client_fixture):
    """Test that we get 400 error on request with invalid uuid."""
    response = await client_fixture.get("/api/v1/file_storage/12395898352")
    assert response.status == web.HTTPBadRequest.status_code


async def test_get_incorrect_uuid(client_fixture, db):
    """Test that we get 404 error on request unknown uuid."""
    response = await client_fixture.get(f"/api/v1/file_storage/{str(uuid4())}")
    assert response.status == web.HTTPNotFound.status_code


async def test_upload_file(client_fixture, db, test_payload):
    """Test that we can put and get some file to storage."""
    put_response = await client_fixture.put(
        "/api/v1/file_storage", data=test_payload
    )
    assert put_response.status == web.HTTPCreated.status_code
    put_payload = await put_response.json()
    link = put_payload["link"]

    get_response = await client_fixture.get(link)
    assert get_response.status == web.HTTPOk.status_code
    get_payload = await get_response.read()
    assert get_payload == test_payload


async def test_upload_same_hash_file(
    client_fixture, db, test_payload, db_connection
):
    """Test that we can put few files with same hash and create only new link."""
    await client_fixture.put("/api/v1/file_storage", data=test_payload)
    await client_fixture.put("/api/v1/file_storage", data=test_payload)
    uploaded_files = await db_connection.fetch("SELECT * FROM uploaded_files")
    assert len(uploaded_files) == 1


async def test_upload_same_hash_file_concurrent(
    client_fixture, db, test_payload, db_connection
):
    """Test that we can put few files concurrently with same hash and create only new link."""
    tasks = (
        client_fixture.put("/api/v1/file_storage", data=test_payload)
        for _ in range(10)
    )
    results = await asyncio.gather(*tasks)
    assert all(
        result.status == web.HTTPCreated.status_code for result in results
    )
    assert len(await db_connection.fetch("SELECT * FROM uploaded_files")) == 1
    assert len(await db_connection.fetch("SELECT * FROM files_meta")) == 10
