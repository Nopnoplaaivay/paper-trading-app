import os
import uuid
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncContextManager
from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.connectors import AsyncSQLServerConnectorPool
from src.common.consts import SQLServerConsts
from src.utils.logger import LOGGER

SESSIONS = {}
DNS = SQLServerConsts.ASYNC_DNS
MIN_CONN = 2
MAX_CONN = 10000

POOL = AsyncSQLServerConnectorPool(dns=DNS, max_conn=MAX_CONN, min_conn=MIN_CONN)

@asynccontextmanager
async def backend_session_scope(new: bool = False) -> AsyncContextManager[AsyncSession]:
    """
    Provide an async transactional scope around a series of operations.
    Shouldn't keep session alive too long, it will block a connection of pool connections.
    """
    session = await POOL.get()
    try:
        yield session
        await session.commit()
    except Exception as exception:
        LOGGER.error(exception, exc_info=True)
        await session.rollback()
        raise exception
    finally:
        await POOL.put(session)