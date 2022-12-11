"""
This module retrieve information from the db to expose through an API
"""

from datetime import datetime
from drivers.timescale.base_driver import BaseDriver
from sqlalchemy.sql import text
from sqlalchemy.future import select
from alembic_files.alembic.models import (
    StockInfo,
    DailyStockPrice,
    WeeklyStockPrice,
    MonthlyStockPrice,
    LastCandle,
)
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
                            select(MonthlyStockPrice)
                            .where(MonthlyStockPrice.symbol == symbol)
                            .where(MonthlyStockPrice.time >= start_operation)
                            .order_by(MonthlyStockPrice.time.asc())
                        ),
                        session.execute(
                            select(LastCandle)
                            .where(LastCandle.symbol == symbol)
                            .where(LastCandle.resolution == "D")
                            .limit(1)
                        ),
                    ]
                )
            else:
                prices = await session.execute(
                    select(MonthlyStockPrice)
                    .where(MonthlyStockPrice.symbol == symbol)
                    .where(MonthlyStockPrice.time >= start_operation)
                    .where(MonthlyStockPrice.time <= end_operation)
                    .order_by(MonthlyStockPrice.time.asc())
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

    async def select_history(self, symbol: str, resolution: str):
        engine, session = await self._create_session()
        async with session() as session:
            if resolution == "D":
                prices = await session.execute(
                    select(DailyStockPrice)
                    .where(DailyStockPrice.symbol == symbol)
                    .order_by(DailyStockPrice.time.asc())
                )
            elif resolution == "W":
                prices = await session.execute(
                    select(WeeklyStockPrice)
                    .where(WeeklyStockPrice.symbol == symbol)
                    .order_by(WeeklyStockPrice.time.asc())
                )

            else:
                prices = await session.execute(
                    select(MonthlyStockPrice)
                    .where(MonthlyStockPrice.symbol == symbol)
                    .order_by(MonthlyStockPrice.time.asc())
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

    async def select_recommendations_by_macd(self):
        query = text(
            """
            select msp2.time, msp.symbol, si.name, msp.close, msp.macd, msp.macd_signal, si.industry from 
            (
            SELECT msp.*, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY time DESC) AS rn
            FROM monthly_stock_price msp
            ) msp 
            inner join (
            SELECT msp2.*, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY time asc) AS rn
            FROM monthly_stock_price msp2
            ) msp2
            on msp.symbol = msp2.symbol
            inner join (
            SELECT wsp.*, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY time desc) AS rn
            FROM weekly_stock_price wsp
            ) wsp 
            on msp.symbol = wsp.symbol
            left join stock_info si
            on si.symbol = msp.symbol
            where msp.macd < msp.macd_signal and wsp.macd > wsp.macd_signal and msp.macd <= 0 and msp.rn = 1 and msp2.rn = 1 and wsp.rn = 1 and msp.close < 210 order by si.industry;
            """
        )
        engine, session = await self._create_session()

        async with session() as session:
            stocks_by_macd = await session.execute(query)

            try:
                stocks_by_macd = [
                    {
                        "start": stock.time.strftime("%Y-%m-%d"),
                        "symbol": stock.symbol,
                        "name": stock.name,
                        "last_close": stock.close,
                        "macd": stock.macd,
                        "macd_signal": stock.macd_signal,
                        "industry": stock.industry,
                    }
                    for stock in stocks_by_macd
                ]

            except NoResultFound:
                ...

            await session.commit()
        await self._close(session, engine)

        return stocks_by_macd

    async def select_symbol_industry(self, symbol: str):
        engine, session = await self._create_session()

        stock_info = None
        async with session() as session:
            stock_info = await session.execute(
                select(StockInfo).where(StockInfo.symbol == symbol)
            )

            try:
                stock_info = stock_info.scalars().one()
                stock_info = stock_info.industry

            except NoResultFound:
                ...

            await session.commit()

        await self._close(session, engine)

        return stock_info

    async def select_symbol_last_price(self, symbol: str):
        engine, session = await self._create_session()

        price = None
        async with session() as session:
            price = await session.execute(
                select(LastCandle)
                .where(LastCandle.symbol == symbol)
                .where(LastCandle.resolution == "D")
                .limit(1)
            )

            try:
                price = price.scalars().one()
                price = price.close

            except NoResultFound:
                ...

            await session.commit()

        await self._close(session, engine)

        return price
