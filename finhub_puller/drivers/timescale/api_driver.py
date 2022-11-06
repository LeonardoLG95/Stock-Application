"""
This module retrieve information from the db to expose through an API
"""

from datetime import datetime
from drivers.timescale.base_driver import BaseDriver
from sqlalchemy.future import select
from alembic_files.alembic.models import StockInfo, StockPrice
from sqlalchemy.exc import NoResultFound
import asyncio


class TimescaleDriver(BaseDriver):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def select_stocks(self):
        engine, session = await self._create_session()

        async with session() as session:
            stocks_list = await session.execute(
                select(StockInfo).order_by(StockInfo.name.asc())
            )

            try:
                stocks_list = [
                    [stock.name, stock.symbol] for stock in stocks_list.scalars()
                ]
            except NoResultFound:
                ...

            await session.commit()
        await self._close(session, engine)

        return stocks_list

    async def select_symbol_prices(
        self,
        symbol: str,
        start_operation: datetime,
        end_operation: datetime,
        resolution: str,
    ):
        engine, session = await self._create_session()
        async with session() as session:
            last_price = None

            if end_operation is None:
                prices, last_price = await asyncio.gather(
                    *[
                        session.execute(
                            select(StockPrice)
                            .where(StockPrice.symbol == symbol)
                            .where(StockPrice.resolution == resolution)
                            .where(StockPrice.time >= start_operation)
                            .order_by(StockPrice.time.asc())
                        ),
                        session.execute(
                            select(StockPrice)
                            .where(StockPrice.symbol == symbol)
                            .where(StockPrice.resolution == "D")
                            .where(StockPrice.time >= start_operation)
                            .order_by(StockPrice.time.desc())
                            .limit(1)
                        ),
                    ]
                )
            else:
                prices = await session.execute(
                    select(StockPrice)
                    .where(StockPrice.symbol == symbol)
                    .where(StockPrice.resolution == resolution)
                    .where(StockPrice.time >= start_operation)
                    .where(StockPrice.time <= end_operation)
                    .order_by(StockPrice.time.asc())
                )

            try:
                prices = [
                    [price.time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), price.close]
                    for price in prices.scalars()
                ]
                if last_price is not None:
                    lp = last_price.scalars().one()
                    prices.append([lp.time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), lp.close])

            except NoResultFound:
                ...

            await session.commit()

        await self._close(session, engine)

        return prices
