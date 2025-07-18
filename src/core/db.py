"""Database module."""

import logging
from collections.abc import Callable
from contextlib import AbstractContextManager, asynccontextmanager
from contextvars import ContextVar, Token
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Mapper, Session, sessionmaker
from sqlalchemy.sql.expression import Delete, Insert, Update

from src.core.config import settings
from src.models.base import Base

logger = logging.getLogger(__name__)


# Context management
session_context: ContextVar[str] = ContextVar('session_context')


def get_session_context() -> str:
    try:
        return session_context.get()
    except LookupError:
        raise


def set_session_context(session_id: str) -> Token:
    return session_context.set(session_id)


def reset_session_context(context: Token) -> None:
    session_context.reset(context)


class Database:
    def __init__(
        self,
        async_db_url: str = settings.WRITER_DB_URL,
        sync_db_url: str = settings.SYNC_DB_URL,
    ) -> None:
        self._async_engine = create_async_engine(
            async_db_url,
            pool_recycle=3600,
            pool_pre_ping=True,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
        )
        self._session_factory = async_sessionmaker(
            class_=AsyncSession,
            sync_session_class=self.get_routing_session(),
            expire_on_commit=False,
        )

        self._engine = create_engine(
            sync_db_url,
            pool_recycle=3600,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )

        self._sync_session_factory = sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )

    def get_routing_session(self) -> Session:
        engine = self._async_engine

        class RoutingSession(Session):
            def get_bind(
                self,
                mapper: Mapper | None = None,
                clause: Any | None = None,
                **kw: Any,
            ) -> Any:
                if self._flushing or isinstance(clause, (Update | Delete | Insert)):
                    return engine.sync_engine
                return engine.sync_engine

        return RoutingSession

    def create_database(self) -> None:
        Base.metadata.create_all(self._engine)

    @asynccontextmanager
    async def session(self) -> Callable[..., AbstractContextManager[AsyncSession]]:
        session: AsyncSession = self._session_factory(expire_on_commit=False)
        try:
            yield session
        except Exception:
            logger.exception('Session rollback because of exception')
            await session.rollback()
            raise
        finally:
            await session.close()

    async def cleanup(self) -> None:
        logger.warning('Closing database connection')
        await self._async_engine.dispose()
        self._engine.dispose()

    def sync_session(self) -> Session:
        return self._sync_session_factory()
