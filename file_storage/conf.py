from pydantic import BaseSettings


class Settings(BaseSettings):
    """App settings."""

    DB_NAME: str = "file_storage"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_SERVER = "localhost"
    DB_PORT = 5432

    TEST_DB_NAME: str = f"test_{DB_NAME}"

    @property
    def postgres_uri(self) -> str:
        """Postgres uri string."""
        return "postgres://{username}:{password}@{address}:{port}/{db_name}".format(
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            address=self.DB_SERVER,
            port=self.DB_PORT,
            db_name=self.DB_NAME,
        )


settings = Settings()
