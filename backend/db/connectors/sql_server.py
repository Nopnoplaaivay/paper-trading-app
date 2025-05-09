import aioodbc
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool

from backend.utils.logger import LOGGER

class AsyncSQLServerConnectorPool:
    def __init__(self, dns: str, max_conn: int, min_conn: int):
        self.dns = dns
        self.max_conn = max_conn
        self.min_conn = min_conn
        self.engine = create_async_engine(
            "mssql+aioodbc://",
            poolclass=AsyncAdaptedQueuePool,
            pool_pre_ping=True,
            pool_size=self.max_conn - self.min_conn,
            max_overflow=self.min_conn,
            pool_timeout=60 * 60,
            async_creator=self.__get_conn__,  # Changed to async_creator
        )
        self.async_session = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def __get_conn__(self):
        """Async connection creator"""
        conn = await aioodbc.connect(dsn=self.dns)
        return conn

    async def get(self) -> AsyncSession:
        """Get an async session from the pool"""
        return self.async_session()

    @classmethod
    async def put(cls, session: AsyncSession):
        """Close the async session"""
        await session.close()

    async def initialize(self):
        """Initialize the connection pool and test the connection"""
        try:
            async with self.get() as session:
                LOGGER.info("Successfully created async connection...")
        except Exception as e:
            raise Exception(f"Could not create connection to {self.dns}", e)
        
    async def close(self):
        """Close the connection pool"""
        await self.engine.dispose()
        LOGGER.info("Connection pool closed")