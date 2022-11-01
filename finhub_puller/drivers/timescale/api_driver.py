"""
This module retrieve information from the db to expose through an API
"""

from datetime import datetime
from drivers.timescale.base_driver import BaseDriver
from sqlalchemy.future import select
from alembic_files.alembic.models import StockInfo, StockPrice
from sqlalchemy.exc import NoResultFound


class TimescaleDriver(BaseDriver):
    def __init__(self, log):
        super().__init__(log=log)

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
            prices = await session.execute(
                (
                    select(StockPrice)
                    .where(StockPrice.symbol == symbol)
                    .where(StockPrice.resolution == resolution)
                    .where(StockPrice.time >= start_operation)
                    .where(StockPrice.time <= end_operation)
                    .order_by(StockPrice.time.asc())
                    if end_operation is not None
                    else select(StockPrice)
                    .where(StockPrice.symbol == symbol)
                    .where(StockPrice.resolution == resolution)
                    .where(StockPrice.time >= start_operation)
                    .order_by(StockPrice.time.asc())
                )
            )

            try:
                prices = [
                    [price.time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), price.close]
                    for price in prices.scalars()
                ]

            except NoResultFound:
                ...

            await session.commit()

        await self._close(session, engine)

        return prices
