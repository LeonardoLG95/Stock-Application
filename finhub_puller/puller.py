import asyncio
from datetime import datetime, timedelta

from drivers.finnhub.finnhub_driver import FinnhubDriver
from finhub_puller.drivers.timescale.puller_driver import TimescaleDriver
from finhub_puller.utils.logger import Logger
from env import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


class Puller:
    def __init__(self):
        self._log = Logger("finhub_puller")
        self._finnhub_driver = FinnhubDriver(self._log)
        self._timescale_driver = TimescaleDriver(
            log=self._log,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            db=DB_NAME,
        )
        self._index_symbols = set()
        self._stock_symbols = set()
        self._resolutions = []

    async def start(self):
        self._index_symbols = self._finnhub_driver.get_index_symbols()
        self._resolutions = self._finnhub_driver.get_resolutions()

        await self._get_symbols()
        await self._timescale_driver.persist_symbols(self._stock_symbols)

    async def _get_symbols(self):
        await asyncio.gather(
            *[
                self._add_symbols_of_index(index_symbol)
                for index_symbol in self._index_symbols
            ]
        )
        self._stock_symbols = self._stock_symbols.union(
            self._finnhub_driver.get_crypto_symbols()
        )

    async def _add_symbols_of_index(self, index_symbol: str):
        index_symbols = await self._finnhub_driver.get_symbols_of_index(index_symbol)
        self._stock_symbols = self._stock_symbols.union(index_symbols)

    def pull_tasks(self):
        self.create_task(function=self.get_and_persist_info(), weeks=4)
        self.create_task(function=self.get_and_persist_financials(), weeks=4)
        self.create_task(
            function=self.get_and_persist_prices(self._resolutions[0]), days=1
        )
        self.create_task(
            function=self.get_and_persist_prices(self._resolutions[1]), weeks=1
        )
        self.create_task(
            function=self.get_and_persist_prices(self._resolutions[2]), weeks=4
        )
        self.create_task(
            function=self.get_and_persists_financial_reports("quarterly"), weeks=4
        )
        self.create_task(
            function=self.get_and_persists_financial_reports("annual"), weeks=4
        )
        self.create_task(function=self._get_symbols(), weeks=1)

    async def get_and_persist_info(self):
        await asyncio.gather(
            *[self._get_info(symbol) for symbol in self._stock_symbols]
        )

    async def _get_info(self, symbol: str):
        info = await self._finnhub_driver.get_symbol_info(symbol)
        if info:
            asyncio.create_task(self._timescale_driver.persist_info(info))

    async def get_and_persist_prices(self, resolution: str):
        await asyncio.gather(
            *[self._get_price(symbol, resolution) for symbol in self._stock_symbols]
        )

    async def _get_price(self, symbol: str, resolution: str):
        price = await self._finnhub_driver.get_symbol_price(symbol, resolution)
        if price:
            asyncio.create_task(self._timescale_driver.persist_historical(price))

    async def get_and_persist_financials(self):
        await asyncio.gather(
            *[self._get_basic_financials(symbol) for symbol in self._stock_symbols]
        )

    async def _get_basic_financials(self, symbol: str):
        basic_financials = await self._finnhub_driver.get_basic_financials(symbol)
        if basic_financials:
            asyncio.create_task(
                self._timescale_driver.persist_basic_financials(basic_financials)
            )

    async def get_and_persists_financial_reports(self, frequency: str):
        await asyncio.gather(
            *[
                self._get_financial_reports(symbol, frequency)
                for symbol in self._stock_symbols
            ]
        )

    async def _get_financial_reports(self, symbol: str, frequency: str):
        reports, concepts = await self._finnhub_driver.get_financial_report(
            symbol, frequency
        )
        if reports and concepts:
            asyncio.create_task(
                self._timescale_driver.persist_financial_reports(
                    reports, concepts, frequency
                )
            )

    def create_task(self, function, **kwargs):
        async def task(f, **k):
            while True:
                self._log.info(f"=> starting task {f.__name__}")
                await f
                now = datetime.now()
                next_repeat = now + timedelta(**k)
                self._log.info(f"=> task {f.__name__} ended ✓")
                await asyncio.sleep(next_repeat.timestamp())

        asyncio.create_task(task(function, **kwargs))

    async def close(self):
        await self._finnhub_driver.close()
