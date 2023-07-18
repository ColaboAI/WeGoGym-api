"""
File with environment variables and general configuration logic.
`SECRET_KEY`, `ENVIRONMENT` etc. map to env variables with the same names.

Pydantic priority ordering:

1. (Most important, will overwrite everything) - environment variables
2. `.env` file in root folder of project
3. Default values

For project name, version, description we use pyproject.toml
For the rest, we use file `.env` (gitignored), see `.env.example`

`DEFAULT_SQLALCHEMY_DATABASE_URI` and `TEST_SQLALCHEMY_DATABASE_URI`:
Both are ment to be validated at the runtime, do not change unless you know
what are you doing. All the two validators do is to build full URI (TCP protocol)
to databases to avoid typo bugs.

See https://pydantic-docs.helpmanual.io/usage/settings/
"""

from functools import lru_cache
from os import environ
from pathlib import Path

from pydantic import AnyHttpUrl, AnyUrl, BaseSettings, validator

PROJECT_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    # CORE SETTINGS
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ENVIRONMENT: str = environ.get(
        "ENV", "DEV"
    )  # Literal["DEV", "PRODUCTION", "STAGING"]
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    BACKEND_CORS_ORIGINS: str | list[AnyHttpUrl]
    REDIS_USERNAME: str = "default"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    REDIS_PASSWORD: str = "password"
    REDIS_URL: str = ""
    # PROJECT NAME, VERSION AND DESCRIPTION
    PROJECT_NAME: str
    VERSION: str
    DESCRIPTION: str

    # POSTGRESQL DEFAULT DATABASE
    DEFAULT_DATABASE_HOSTNAME: str = "localhost"
    DEFAULT_DATABASE_USER: str
    DEFAULT_DATABASE_PASSWORD: str
    DEFAULT_DATABASE_PORT: str
    DEFAULT_DATABASE_DB: str
    DEFAULT_SQLALCHEMY_DATABASE_URI: str = ""

    S3_BUCKET: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    DISCORD_WEBHOOK_URL: str

    # VALIDATORS
    @validator("BACKEND_CORS_ORIGINS")
    def _assemble_cors_origins(cls, cors_origins: str | list[AnyHttpUrl]):
        if isinstance(cors_origins, str):
            return [item.strip() for item in cors_origins.split(",")]
        return cors_origins

    @validator("REDIS_URL")
    def _assemble_redis_url(cls, v: str, values: dict[str, str]) -> str:
        if environ.get("ENV", None) == None:
            return AnyUrl.build(
                scheme="redis",
                user=values["REDIS_USERNAME"],
                password=values["REDIS_PASSWORD"],
                host="localhost",
                port=values["REDIS_PORT"],
            )
        return AnyUrl.build(
            scheme="redis",
            password=values["REDIS_PASSWORD"],
            host=values["REDIS_HOST"],
            port=values["REDIS_PORT"],
        )

    @validator("DEFAULT_SQLALCHEMY_DATABASE_URI")
    def _assemble_default_db_connection(cls, v: str, values: dict[str, str]) -> str:
        if environ.get("ENV", None) == None:
            return AnyUrl.build(
                scheme="postgresql+asyncpg",
                user=values["DEFAULT_DATABASE_USER"],
                password=values["DEFAULT_DATABASE_PASSWORD"],
                host="localhost",
                port=values["DEFAULT_DATABASE_PORT"],
                path=f"/{values['DEFAULT_DATABASE_DB']}",
            )
        return AnyUrl.build(
            scheme="postgresql+asyncpg",
            user=values["DEFAULT_DATABASE_USER"],
            password=values["DEFAULT_DATABASE_PASSWORD"],
            host=values["DEFAULT_DATABASE_HOSTNAME"],
            port=values["DEFAULT_DATABASE_PORT"],
            path=f"/{values['DEFAULT_DATABASE_DB']}",
        )

    class Config:
        env_file = f"{PROJECT_DIR}/.env"
        case_sensitive = True


# dev config for local development


class ProductionSettings(Settings):
    class Config:
        env_file = f"{PROJECT_DIR}/.env.prod"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    if Settings().ENVIRONMENT == "DEV":
        return Settings()
    return ProductionSettings()


settings: Settings = get_settings()
