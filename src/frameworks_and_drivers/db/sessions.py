import logging
from collections.abc import AsyncGenerator, Callable, Generator
from contextlib import AbstractContextManager, asynccontextmanager, contextmanager
from typing import Any

from fastapi import HTTPException
from frameworks_and_drivers.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)

sync_engine = create_engine(settings.db_url, echo=settings.DEBUG)
sync_database_session = sessionmaker(autocommit=False, autoflush=True, bind=sync_engine)

engine = create_async_engine(settings.db_url_async_sqlalchemy, future=True, echo=settings.DEBUG)
async_database_session = sessionmaker(engine, autoflush=True, expire_on_commit=False, class_=AsyncSession)


def get_sync_db() -> Generator[Session, None, None]:
    session: Session = sync_database_session()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as sql_ex:
        logger.debug(f"SQLAlchemy session rollback from sql_ex: {sql_ex}")
        session.rollback()
        raise sql_ex
    except HTTPException as http_ex:
        logger.debug(f"SQLAlchemy session rollback from http_ex: {http_ex}")
        session.rollback()
        raise http_ex
    finally:
        session.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_database_session() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as sql_ex:
            await session.rollback()
            raise sql_ex
        except HTTPException as http_ex:
            await session.rollback()
            raise http_ex
        finally:
            await session.close()


get_db_sync_context_manager: Callable[[], AbstractContextManager[Session]] = contextmanager(get_sync_db)
get_db_async_context_manager = asynccontextmanager(get_async_db)


def _todict(obj: Any) -> dict[Any, Any]:
    """Return the object's dict excluding private attributes,
    sqlalchemy state and relationship attributes.
    """
    excl = ("_sa_adapter", "_sa_instance_state")
    return {k: v for k, v in vars(obj).items() if not k.startswith("_") and not any(hasattr(v, a) for a in excl)}


class BaseSQLAlchemy:
    def __repr__(self) -> str:
        params = ", ".join(f"{k}={v}" for k, v in _todict(self).items())
        return f"{self.__class__.__name__}({params})"


Base = declarative_base(cls=BaseSQLAlchemy)
