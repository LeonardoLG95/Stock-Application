from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio


class BaseDriver:
    def __init__(
        self,
        log,
        user: str = "postgres",
        password: str = "password1234",
        host: str = "localhost",
        port: str = "5500",
        db: str = "stock",
    ):
        self.dsn = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
        self.log = log
        self._semaphore = asyncio.Semaphore(10)

    async def _create_session(self):
        await self._semaphore.acquire()
        engine = create_async_engine(self.dsn, pool_size=100)  # , echo=True
        return engine, sessionmaker(engine, expire_on_commit=True, class_=AsyncSession)

    async def _close(self, session, engine):
        await session.close()
        await engine.dispose()
        self._semaphore.release()
