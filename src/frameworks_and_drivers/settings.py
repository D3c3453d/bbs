from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = False
    API_V0_STR: str = "/api/v0"
    LOG_LEVEL: str = "INFO"
    LOGGER_NAME: str = "app_logger"

    PG_HOST: str = Field(alias="POSTGRES_HOST")
    PG_PORT: int = Field(alias="POSTGRES_PORT")
    PG_USER: str = Field(alias="POSTGRES_USER")
    PG_PASS: str = Field(alias="POSTGRES_PASSWORD")
    PG_DB: str = Field(alias="POSTGRES_DB")
    PG_DB_TEST: str = Field(alias="POSTGRES_DB_TEST", default="test")

    @property
    def postgres_url(self) -> str:
        return f"{self.PG_USER}:{self.PG_PASS}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"

    @property
    def db_url(self) -> str:
        return f"postgresql://{self.postgres_url}"

    @property
    def db_url_async_sqlalchemy(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_url}"

    @property
    def test_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.PG_USER}:{self.PG_PASS}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB_TEST}"

    @property
    def db_url_alembic(self) -> str:
        return f"postgresql+psycopg2://{self.postgres_url}"

    class Config:
        case_sensitive = True


settings = Settings()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(name)s %(funcName)s %(message)s %(pathname)s %(lineno)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": settings.LOG_LEVEL,
        },
    },
    "loggers": {
        "app_logger": {
            "handlers": ["console"],
            "level": settings.LOG_LEVEL,
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": settings.LOG_LEVEL,
        },
    },
}
