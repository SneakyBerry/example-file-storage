import asyncio
from random import randint

import asyncpg
import pytest
from aiohttp.test_utils import TestClient
from file_storage.app import get_application
from file_storage.conf import settings
from file_storage.setup import get_db
from yoyo import get_backend, read_migrations


@pytest.fixture()
def test_payload():
    return b"".join(str(randint(0, 100)).encode() for _ in range(100))


@pytest.fixture()
def client_fixture(aiohttp_client, loop) -> TestClient:
    """Fixture with client."""
    app = get_application()
    new_client = loop.run_until_complete(aiohttp_client(app))
    return new_client


@pytest.fixture()
async def db_connection(client_fixture) -> asyncpg.Connection:
    """Connection to postgres db."""
    # db setup is made only after application started,
    # so we have to use `client` here to have application initialized.
    connection: asyncpg.Connection
    async with client_fixture.app.db.acquire() as connection:
        async with connection.transaction():
            yield connection


@pytest.fixture()
async def db(db_connection):
    """Truncate all tables (except yoyo migrations) after each test."""
    try:
        yield
    finally:
        await db_connection.execute(
            """
                CREATE OR REPLACE FUNCTION truncate_tables() RETURNS void AS $$
                DECLARE
                    statements CURSOR FOR
                        SELECT tablename FROM pg_tables
                        WHERE schemaname = 'public' and tablename not like '%yoyo%';
                BEGIN
                    FOR stmt IN statements LOOP
                        EXECUTE 'TRUNCATE TABLE ' || quote_ident(stmt.tablename) || ' CASCADE;';
                    END LOOP;
                END;
                $$ LANGUAGE plpgsql;
            """,
        )
        await db_connection.execute("select truncate_tables();")


@pytest.fixture(scope="session", autouse=True)
def _setup_teardown_postgres():
    """Setup test database and drop it after test run."""
    loop = asyncio.get_event_loop()

    # Connect to EXISTING db, because no one can't delete db if he is connected to it
    db_pool = loop.run_until_complete(get_db())
    connection = loop.run_until_complete(db_pool.acquire())
    # Drop test db (after previous test runs)
    loop.run_until_complete(
        connection.execute(
            f"DROP DATABASE IF EXISTS {settings.TEST_DB_NAME};"
        ),
    )
    # And create a new one the same
    loop.run_until_complete(
        connection.execute(f"CREATE DATABASE {settings.TEST_DB_NAME};")
    )
    loop.run_until_complete(db_pool.release(connection))

    # Run migrations
    backend = get_backend(
        "postgresql://{user}:{password}@{host}:{port}/{db}".format(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_SERVER,
            port=settings.DB_PORT,
            db=settings.TEST_DB_NAME,
        ),
    )
    migrations = read_migrations("file_storage/migrations")
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
    del backend  # connection is not released in other case

    # mock original db name with test db name
    settings.DB_NAME = settings.TEST_DB_NAME
    # Run tests for whole session
    yield

    # Drop test db
    connection = loop.run_until_complete(db_pool.acquire())
    loop.run_until_complete(
        connection.execute(
            f"DROP DATABASE IF EXISTS {settings.TEST_DB_NAME};"
        ),
    )
    loop.run_until_complete(db_pool.release(connection))
    loop.run_until_complete(db_pool.close())
