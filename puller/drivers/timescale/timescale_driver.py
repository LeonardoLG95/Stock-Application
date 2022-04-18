import asyncio
from typing import Set, List

from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import update

from stock_utils.models.classes import StockInfo, Symbol, StockPrice, LastCandle


class TimescaleDriver:
    def __init__(self, log, user: str = 'postgres', password: str = 'password1234',
                 host: str = 'localhost', port: str = '5500', db: str = 'stock'):
        self.dsn = f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}'
        self.log = log
        self._semaphore = asyncio.Semaphore(10)

    async def _create_session(self):
        await self._semaphore.acquire()
        engine = create_async_engine(self.dsn, pool_size=100)  # , echo=True
        return engine, sessionmaker(engine, expire_on_commit=True,
                                    class_=AsyncSession)

    async def persist_symbols(self, symbols: Set[str]):
        if not symbols:
            return

        engine, session = await self._create_session()
        async with session() as session:
            for symbol in symbols:
                select_result = await session.execute(select(Symbol).where(Symbol.symbol.in_([symbol])))
                try:
                    select_result.scalars().one()
                except NoResultFound:
                    self.log.info(f'persisting symbol {symbol}')
                    session.add(Symbol(symbol=symbol))

            await session.commit()

        await self._close(session, engine)

    async def persist_info(self, info: StockInfo):
        if not isinstance(info, StockInfo):
            return

        to_update = await self._check_and_insert_info(info)
        if to_update:
            await self._update_info(info)

    async def _check_and_insert_info(self, info: StockInfo):
        to_update = False

        engine, session = await self._create_session()
        async with session() as session:
            select_result = await session.execute(
                select(StockInfo)
                    .where(StockInfo.symbol == info.symbol))
            try:
                select_result = select_result.scalars().one()
                if int(select_result.market_capitalization) != int(info.market_capitalization) \
                        and int(select_result.share_outstanding) != int(info.share_outstanding):
                    to_update = True

            except NoResultFound:
                self.log.info(f'persisting info of {info.name}')
                session.add(info)

            await session.commit()

        await self._close(session, engine)

        return to_update

    async def _update_info(self, info: StockInfo):
        self.log.info(f'updating info of symbol {info.name}')

        engine, session = await self._create_session()
        async with session() as session:
            update_result = await session.execute(
                update(StockInfo).where(StockInfo.symbol == info.symbol).values(dict(info))
            )
            if update_result.rowcount == 0:
                session.add(StockInfo(**dict(info)))

            await session.commit()

        await self._close(session, engine)

    async def persist_historical(self, historical: List[StockPrice]):
        if not isinstance(historical, list):
            return

        symbol = historical[0].symbol
        resolution = historical[0].resolution
        self.log.info(f'persisting price of {symbol} with resolution {resolution}')

        new_symbol, last_candle_time = await self._check_historical(symbol, resolution)

        if new_symbol:
            historical.append(LastCandle(**dict(historical[len(historical) - 1])))
            await self._add_all(historical)
        else:
            remaining_historical, price_to_update = self._filter_historical(historical, last_candle_time)
            await self._persist_remaining_historical(remaining_historical, price_to_update)

    async def _check_historical(self, symbol: str, resolution: str):
        new_symbol = False
        last_candle_time = None

        engine, session = await self._create_session()
        async with session() as session:
            last_candle = await session.execute(
                select(StockPrice)
                    .where(StockPrice.symbol == symbol)
                    .where(StockPrice.resolution == resolution)
                    .order_by(StockPrice.time.desc()).limit(1)
                )

            try:
                last_candle = last_candle.scalars().one()

                last_candle_time = last_candle.time

            except NoResultFound:
                new_symbol = True

            await session.commit()
        await self._close(session, engine)

        return new_symbol, last_candle_time

    @staticmethod
    def _filter_historical(historical: List[StockPrice], last_candle_time):
        price_to_update = None
        remaining_historical = []

        for price in historical:
            if price.time < last_candle_time:
                continue
            elif price.time.date() == last_candle_time.date():
                price_to_update = price

            else:
                remaining_historical.append(price)

        return remaining_historical, price_to_update

    async def _persist_remaining_historical(self, historical: List[StockPrice],
                                            price_to_update: StockPrice):
        if historical:
            await self._add_all(historical)
            last_candle = LastCandle(**dict(historical[len(historical) - 1]))
        else:
            last_candle = LastCandle(**dict(price_to_update))

        await self._update_stock_price(price_to_update)
        await self._update_last_candle(last_candle)

    async def _update_stock_price(self, price_to_update: StockPrice):
        engine, session = await self._create_session()
        async with session() as session:
            update_result = await session.execute(
                update(StockPrice)
                    .where(StockPrice.symbol == price_to_update.symbol)
                    .where(StockPrice.resolution == price_to_update.resolution)
                    .where(StockPrice.time == price_to_update.time)
                    .values(dict(price_to_update))
            )

            if update_result.rowcount == 0:
                session.add(StockPrice(**dict(price_to_update)))

            await session.commit()

        await self._close(session, engine)

    async def _update_last_candle(self, last_candle: LastCandle):
        engine, session = await self._create_session()
        async with session() as session:
            update_result = await session.execute(
                update(LastCandle)
                    .where(LastCandle.symbol == last_candle.symbol)
                    .where(LastCandle.resolution == last_candle.resolution)
                    .values(dict(last_candle))
            )

            if update_result.rowcount == 0:
                session.add(LastCandle(**dict(last_candle)))

            await session.commit()

        await self._close(session, engine)

    async def _add_all(self, list_of_objects: list):
        engine, session = await self._create_session()
        async with session() as session:
            try:
                session.add_all(list_of_objects)
            except IntegrityError as exc:
                self.log.error(exc)

            await session.commit()

        await self._close(session, engine)

    async def _close(self, session, engine):
        await session.close()
        await engine.dispose()
        self._semaphore.release()
