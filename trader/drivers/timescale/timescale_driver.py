from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from utils.models import Symbol, StockPrice, BasicFinancials
from sqlalchemy import select


class TimescaleDriver:
    def __init__(self, user: str = 'postgres', password: str = 'password1234',
                 host: str = 'localhost', port: str = '5500', db: str = 'stock'):
        self.dsn = f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}'

    async def _create_session(self):
        engine = create_async_engine(self.dsn, pool_size=100)  # , echo=True
        return engine, sessionmaker(engine, expire_on_commit=False,
                                    class_=AsyncSession)

    async def select_symbols(self):
        engine, session = await self._create_session()
        async with session() as session:
            async with session.begin():
                symbols = await session.execute(
                    select(Symbol)
                )
                try:
                    symbols = symbols.fetchall()

                except NoResultFound:
                    ...

        await self._close(session, engine)

        if symbols:
            return [row['Symbol'] for row in symbols]

    async def select_prices(self, symbol: str, resolution: str):
        engine, session = await self._create_session()
        async with session() as session:
            async with session.begin():
                historic = await session.execute(
                    select(StockPrice)
                    .where(StockPrice.symbol == symbol)
                    .where(StockPrice.resolution == resolution)
                    .order_by(StockPrice.time.asc())
                )
                try:
                    historic = historic.fetchall()

                except NoResultFound:
                    ...

        await self._close(session, engine)

        if historic:
            return [row['StockPrice'] for row in historic]

    async def select_basic_info(self, symbol: str, time_window: str):
        engine, session = await self._create_session()
        async with session() as session:
            async with session.begin():
                basic_financials = await session.execute(
                    select(BasicFinancials)
                    .where(BasicFinancials.symbol == symbol)
                    .where(BasicFinancials.time_window == time_window)
                    .order_by(BasicFinancials.period.asc())
                )
                try:
                    basic_financials = basic_financials.fetchall()

                except NoResultFound:
                    ...

        await self._close(session, engine)

        if basic_financials:
            return [row['BasicFinancials'] for row in basic_financials]

    @staticmethod
    async def _close(session, engine):
        await session.close()
        await engine.dispose()
