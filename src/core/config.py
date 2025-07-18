"""Settings module for the application."""

import os
from enum import StrEnum
from typing import List

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# env file on root directory
DOTENV_PATH = os.path.join(os.path.dirname(__file__), '../../.env')


class Env(StrEnum):
    """Enumeration for different environments."""

    dev = 'dev'
    prod = 'prod'
    local = 'local'


class Settings(BaseSettings):
    """Settings class for the application.

    This class is responsible for loading and managing application
    configuration settings from environment variables and a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=DOTENV_PATH,
        env_ignore_empty=True,
        extra='ignore',
    )
    ENVIRONMENT: Env = Env.local
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: str = '5435'
    POSTGRES_DB: str = 'momos'
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DOWNLOAD_FILE_CHUNK_SIZE: int = 4096  # 4KB

    # DB lock
    TRANSACTION_LOCK_ID: int = 1433

    # Constants
    MAX_ALLOW_FLOAT_DIFF: float = 1e-6

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = []

    # Logging
    LOG_LEVEL: str = 'INFO'
    LOG_OUTPUT: str = 'logs'

    @computed_field
    def WRITER_DB_URL(self) -> str:
        """Construct the database URL for writing."""
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    @computed_field
    def SYNC_DB_URL(self) -> str:
        """Construct the database URL for synchronous operations."""
        return f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'


settings = Settings()
