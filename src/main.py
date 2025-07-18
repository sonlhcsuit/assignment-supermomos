from contextlib import asynccontextmanager

from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.requests import Request

from src.api.routers.common import common_router
from src.container import Container
from src.core.config import settings
from src.core.db import Database
from src.core.logger import setup_logging
from src.custom_app import CustomAPIApp
from src.schemas.base_response import BaseResponse
from src.schemas.exceptions.base import AppException


@asynccontextmanager
@inject
async def lifespan(
    app: CustomAPIApp,
    db: Database = Provide[Container.db],
):
    """Lifespan event handler for the FastAPI application.

    This function is called when the application starts up and shuts down.
    It initializes the dependency injection container and performs any
    necessary setup or teardown tasks.

    Args:
        app (CustomAPIApp): The FastAPI application instance.
        db: The database instance from the dependency injection container.
    """
    # Initialize any resources or services here if needed
    yield
    # Cleanup code can be added here if needed
    # Call cleanup function of injected db
    await db.cleanup()


def init_router(app_: FastAPI):
    """Initialize the routers for the FastAPI application.

    This function sets up the API routers for the application, allowing
    for modular organization of routes and endpoints.

    Args:
        app_ (FastAPI): The FastAPI application instance.
    """
    routers = [common_router]

    for router in routers:
        app_.include_router(router)


def init_middleware(app_: FastAPI):
    """Initialize middleware for the FastAPI application."""
    # Add middleware here if needed
    origins = [
        '*',
    ]
    app_.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,  # Allow cookies, authorization headers, etc.
        allow_methods=['*'],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
        allow_headers=['*'],  # Allow all headers
    )


def init_listeners(app_: FastAPI) -> None:
    @app_.exception_handler(Exception)
    async def universal_exception_handler(request: Request, exc: Exception):
        return ORJSONResponse(
            status_code=500,
            content=BaseResponse.error(exc).model_dump(),
        )

    # Exception handler
    @app_.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return ORJSONResponse(
            status_code=exc.error_code.value,
            content=BaseResponse.error(exc).model_dump(),
        )


def create_app() -> CustomAPIApp:
    """Create and configure the FastAPI application.

    This function initializes the FastAPI application, sets up the
    dependency injection container, and configures the application
    with necessary middleware, routes, and other settings.

    Returns:
        CustomAPIApp: The configured FastAPI application instance.
    """
    app = CustomAPIApp(
        title='My FastAPI Application',
        description='A FastAPI application with dependency injection and custom configurations.',
        version='1.0.0',
        lifespan=lifespan,
        docs_url='/docs' if settings.ENVIRONMENT == 'local' else None,
        redoc_url='/redoc' if settings.ENVIRONMENT == 'local' else None,
        openapi_url='/openapi.json' if settings.ENVIRONMENT == 'local' else None,
    )

    # Initialize middleware
    init_middleware(app)

    # Initialize event handlers
    init_listeners(app)

    # Initialize routers
    init_router(app)

    # Register the container with the app
    app.container = Container()

    return app


setup_logging()
app = create_app()
