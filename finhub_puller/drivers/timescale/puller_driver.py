import asyncio
from typing import Set, List, Tuple

from sqlalchemy.exc import NoResultFound, IntegrityError

from sqlalchemy.future import select
from sqlalchemy.sql.expression import update

from finhub_puller.alembic_files.alembic.models import (
    StockInfo,
    Symbol,
    StockPrice,
    LastCandle,
    BasicFinancials,
    FinancialReport,
    ReportConcept,
)
from drivers.timescale.base_driver import BaseDriver


class TimescaleDriver(BaseDriver):
    async def persist_symbols(self, symbols: Set[str]):
        if not symbols:
            return

        engine, session = await self._create_session()
        async with session() as session:
            for symbol in symbols:
                select_result = await session.execute(
                    select(Symbol).where(Symbol.symbol.in_([symbol]))
                )
                try:
                    select_result.scalars().one()
                except NoResultFound:
                    self.log.info(f"persisting symbol {symbol}")
                    session.add(Symbol(symbol=symbol))

            await session.commit()

        await self._close(session, engine)

    async def persist_info(self, info: dict):
        if not isinstance(info, dict):
            return

        to_update = await self._check_and_insert_info(info)
        if to_update:
            await self._update_info(info)

    async def _check_and_insert_info(self, info: dict):
        to_update = False

        engine, session = await self._create_session()
        async with session() as session:
            select_result = await session.execute(
                select(StockInfo).where(StockInfo.symbol == info["symbol"])
            )
            try:
                select_result = select_result.scalars().one()
                if int(select_result.market_capitalization) != int(
                    info["market_capitalization"]
                ) and int(select_result.share_outstanding) != int(
                    info["share_outstanding"]
                ):
                    to_update = True

            except NoResultFound:
                self.log.info(f'persisting info of {info["name"]}')
                session.add(StockInfo(**info))

            await session.commit()

        await self._close(session, engine)

        return to_update

    async def _update_info(self, info: dict):
        self.log.info(f'updating info of symbol {info["name"]}')

        engine, session = await self._create_session()
        async with session() as session:
            await session.execute(
                update(StockInfo).where(StockInfo.symbol == info["symbol"]).values(info)
            )

            await session.commit()

        await self._close(session, engine)

    async def persist_historical(self, historical: Tuple[dict]):
        if not isinstance(historical, tuple):
            return

        historical = list(historical)

        symbol = historical[0]["symbol"]
        resolution = historical[0]["resolution"]

        self.log.info(f"persisting price of {symbol} with resolution {resolution}")

        last_candle_time = await self._check_historical(symbol, resolution)

        if not last_candle_time:
            last_candle = LastCandle(**historical[len(historical) - 1])
            historical_objects = [StockPrice(**price) for price in historical]
            historical_objects.append(last_candle)
            await self._add_all(historical_objects)
        else:
            remaining_historical, price_to_update = self._filter_historical(
                historical, last_candle_time
            )
            await self._persist_remaining_historical(
                remaining_historical, price_to_update
            )

    async def _check_historical(self, symbol: str, resolution: str):
        last_candle_time = None

        engine, session = await self._create_session()
        async with session() as session:
            last_candle = await session.execute(
                select(StockPrice)
                .where(StockPrice.symbol == symbol)
                .where(StockPrice.resolution == resolution)
                .order_by(StockPrice.time.desc())
                .limit(1)
            )

            try:
                last_candle = last_candle.scalars().one()

                last_candle_time = last_candle.time

            except NoResultFound:
                ...

            await session.commit()
        await self._close(session, engine)

        return last_candle_time

    @staticmethod
    def _filter_historical(
        historical: List[dict], last_candle_time
    ) -> Tuple[Tuple[dict], dict]:
        price_to_update = None
        remaining_historical = ()

        same_date = False
        for price in historical:
            if price["time"].date() < last_candle_time.date():
                continue
            elif price["time"].date() == last_candle_time.date():
                if not same_date:
                    price_to_update = price
                    same_date = True

            else:
                remaining_historical += (price,)

        return remaining_historical, price_to_update

    async def _persist_remaining_historical(
        self, historical: Tuple[dict], price_to_update: dict
    ):
        if historical:
            await self._add_all([StockPrice(**price) for price in historical])

            last_candle = historical[len(historical) - 1]
        else:
            last_candle = price_to_update

        await self._update_stock_price(price_to_update)
        await self._update_last_candle(last_candle)

    async def _update_stock_price(self, price_to_update: dict):
        engine, session = await self._create_session()
        async with session() as session:
            update_result = await session.execute(
                update(StockPrice)
                .where(StockPrice.symbol == price_to_update["symbol"])
                .where(StockPrice.resolution == price_to_update["resolution"])
                .where(StockPrice.time == price_to_update["time"])
                .values(price_to_update)
            )

            if update_result.rowcount == 0:
                session.add(StockPrice(**price_to_update))

            await session.commit()

        await self._close(session, engine)

    async def _update_last_candle(self, last_candle: dict):
        engine, session = await self._create_session()
        async with session() as session:
            update_result = await session.execute(
                update(LastCandle)
                .where(LastCandle.symbol == last_candle["symbol"])
                .where(LastCandle.resolution == last_candle["resolution"])
                .values(last_candle)
            )

            if update_result.rowcount == 0:
                session.add(LastCandle(**last_candle))

            await session.commit()

        await self._close(session, engine)

    async def persist_basic_financials(self, financials: tuple):
        if not isinstance(financials, tuple):
            return

        financials = list(financials)
        symbol = financials[0]["symbol"]

        last_quarterly_period, last_annual_period = await asyncio.gather(
            self._check_last_financials_persisted(symbol, "quarterly"),
            self._check_last_financials_persisted(symbol, "annual"),
        )

        if last_quarterly_period is None and last_annual_period is None:
            await self._add_all(
                [BasicFinancials(**financial) for financial in financials]
            )
            return
        await self._persist_remaining_financials(
            financials, last_quarterly_period, last_annual_period
        )

    async def _check_last_financials_persisted(self, symbol: str, time_window: str):
        last_financial_time = None

        engine, session = await self._create_session()
        async with session() as session:
            last_financials = await session.execute(
                select(BasicFinancials)
                .where(BasicFinancials.symbol == symbol)
                .where(BasicFinancials.time_window == time_window)
                .order_by(BasicFinancials.period.desc())
                .limit(1)
            )

            try:
                last_financials = last_financials.scalars().one()
                last_financial_time = last_financials.period

            except NoResultFound:
                ...

            await session.commit()
        await self._close(session, engine)

        return last_financial_time

    async def _persist_remaining_financials(
        self, financials: list, quarterly_period, annual_period
    ):
        remaining_financials = []
        for financial in financials:
            if (
                financial["time_window"] == "quarterly"
                and financial["period"] > quarterly_period
            ):
                remaining_financials.append(financial)

            if (
                financial["time_window"] == "annual"
                and financial["period"] > annual_period
            ):
                remaining_financials.append(financial)

        if remaining_financials:
            await self._add_all(
                [BasicFinancials(**financial) for financial in remaining_financials]
            )

    async def persist_financial_reports(
        self, reports: Tuple[dict], concepts: Tuple[dict], frequency: str
    ):
        if not isinstance(reports, tuple):
            return

        reports, last_id_not_persisted = await self._check_reports_and_get_id(
            reports, frequency
        )
        if not reports:
            return

        if not isinstance(concepts, tuple):
            return

        concepts = await self._check_concepts(concepts, last_id_not_persisted)
        if not concepts:
            return

        full_reports = reports + concepts
        if full_reports:
            await self._add_all(full_reports)

    async def _check_reports_and_get_id(self, reports: Tuple[dict], frequency: str):
        """Persist reports and return the first non persisted id"""
        reports = list(reports)
        symbol = reports[0]["symbol"]

        last_year, last_quarter = await self._check_last_report_persisted(
            symbol, frequency
        )
        if not last_year:
            return [FinancialReport(**report) for report in reports], None

        if frequency == "annual":
            remaining_reports = [
                report for report in reports if report.get("year") > last_year
            ]
        else:
            remaining_reports = [
                report
                for report in reports
                if report.get("year") >= last_year
                and report.get("quarter") > last_quarter
            ]

        if remaining_reports:
            return [
                FinancialReport(**report) for report in remaining_reports
            ], remaining_reports[0].get("id")

        return None, None

    async def _check_last_report_persisted(self, symbol: str, frequency):
        last_year = None
        last_quarter = None

        engine, session = await self._create_session()
        async with session() as session:
            last_report = await session.execute(
                select(FinancialReport)
                .where(FinancialReport.symbol == symbol)
                .where(FinancialReport.frequency == frequency)
                .order_by(FinancialReport.year.desc())
                .order_by(FinancialReport.quarter.desc())
                .limit(1)
            )

            try:
                last_report = last_report.scalars().one()

                last_year = last_report.year
                last_quarter = last_report.quarter

            except NoResultFound:
                ...

            await session.commit()
        await self._close(session, engine)

        return last_year, last_quarter

    @staticmethod
    async def _check_concepts(concepts: Tuple[dict], report_id: str):
        concepts = list(concepts)

        if not report_id:
            return [ReportConcept(**concept) for concept in concepts]

        remaining_concepts = []
        # When pull from the api, the order is desc, after the access number persisted, the rest is old
        for i, concept in enumerate(concepts):
            if concept.get("financial_report") == report_id:
                break

            remaining_concepts.append(concept)

        return [ReportConcept(**concept) for concept in remaining_concepts]

    async def _add_all(self, list_of_objects: list):
        engine, session = await self._create_session()
        async with session() as session:
            try:
                session.add_all(list_of_objects)
            except IntegrityError as exc:
                self.log.error(exc)

            await session.commit()

        await self._close(session, engine)
