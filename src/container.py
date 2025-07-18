"""Container module for Dependency Injection.

This module defines a Dependency Injection container using the
dependency_injector library. It includes the configuration for
services, repositories, and other components of the application.
This container is responsible for managing the lifecycle of
dependencies and providing them to the application as needed.
"""

from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Factory, Singleton
from services.user import UserService

from src.core.config import settings
from src.core.db import Database
from src.repos import UserRepo
# from src.services.file import FileService
# from src.services.jdy.manpower_calculator import ManpowerCalculator
# from src.services.jdy.update import ManpowerUpdateService
# from src.services.metadata import MetadataService
# from src.services.process import DataProcessingService
# from src.services.storage.client import StorageClient


class Container(DeclarativeContainer):
    """Dependency Injection Container for the application.

    This container is responsible for managing the lifecycle of application
    components, including services, repositories, and other dependencies.
    It uses the `dependency_injector` library to provide a clean and efficient
    way to manage dependencies and their configurations.
    """

    wiring_config = WiringConfiguration(
        modules=[
            'src.api',
            'src.services',
            'src.main',
            'src.api.routers',
            'src.api.routers.common',
            'src.api.query',
            'src.services.user',
        ],
    )

    # Core services
    db = Singleton(
        Database,
        async_db_url=settings.WRITER_DB_URL,
        sync_db_url=settings.SYNC_DB_URL,
    )

    user_repo = Factory(
        UserRepo,
        db=db
    )

    # Service
    user_service = Factory(
        UserService,
        user_repo
    )