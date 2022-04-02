import asyncio
from datetime import datetime, timedelta

from drivers.finnhub.finnhub_driver import FinnhubDriver
from drivers.timescale.timescale_driver import TimescaleDriver
from logger import Logger


class Puller:
    def __init__(self):
        log = Logger('puller')
        self._finnhub_driver = FinnhubDriver(log)
        self._timescale_driver = TimescaleDriver(log)
        self._now = datetime.now()
        self._waiting_time = 60
        self._index_symbols = set()
        self._semaphore = asyncio.Semaphore(60)
        self.stock_symbols = set()
        self.resolutions = []

    async def start(self):
        self._index_symbols = self._finnhub_driver.get_index_symbols()
        self.resolutions = self._finnhub_driver.get_resolutions()
        asyncio.create_task(self._update_time_task())

        await self._timescale_driver.connect()
        await asyncio.gather(
            self._timescale_driver.create_last_candle_table(),
            self._get_symbols()
        )

    async def _update_time_task(self):
        while True:
            self._now = datetime.now()
            await asyncio.sleep(60)

    async def rehydrate_symbols(self):
        while True:
            await self._get_symbols()

            await asyncio.sleep(1000)

    async def _get_symbols(self):
        await asyncio.gather(*[
            self._add_symbols_for_index(index_symbol)
            for index_symbol in self._index_symbols
        ])
        self.stock_symbols.add(self._finnhub_driver.get_crypto_symbols())

    async def _add_symbols_for_index(self, index_symbol: str):
        await self._semaphore.acquire()

        index_symbols = await self._finnhub_driver.get_symbols_of_index(index_symbol)
        self.stock_symbols = self.stock_symbols.union(index_symbols)
        await asyncio.sleep(self._waiting_time)

        self._semaphore.release()

    async def daily_task_data_from_all_symbols(self):
        while True:
            await self._get_and_persist_data_for_all_symbols(self.resolutions[0])
            now = self._now.timestamp()
            next_day = self._now + timedelta(days=1)

            await asyncio.sleep(next_day.timestamp() - now)

    async def weekly_task_data_from_all_symbols(self):
        while True:
            await self._get_and_persist_data_for_all_symbols(self.resolutions[1])
            now = self._now.timestamp()
            next_week = self._now + timedelta(weeks=1)

            await asyncio.sleep(next_week.timestamp() - now)

    async def monthly_task_data_from_all_symbols(self):
        while True:
            await self._get_and_persist_data_for_all_symbols(self.resolutions[2])
            now = self._now.timestamp()
            next_month = self._now + timedelta(weeks=1)

            await asyncio.sleep(next_month.timestamp() - now)

    async def _get_and_persist_data_for_all_symbols(self, resolution: str):
        symbol_chunk = []
        petitions = 0
        for i, stock_symbol in enumerate(self.stock_symbols):
            if petitions < 59:
                petitions += 1
                symbol_chunk.append(stock_symbol)
                if i + 1 != len(self.stock_symbols):
                    continue

            stock_historical = await asyncio.gather(*[self._get_data(symbol, resolution)
                                                      for symbol in symbol_chunk
                                                      ])

            for j, historical in enumerate(stock_historical):
                asyncio.create_task(
                    self._persist_symbol_resolution_data(symbol_chunk[j], resolution, historical)
                )

            symbol_chunk = []
            petitions = 0

    async def _get_data(self, symbol: str, resolution: str):
        await self._semaphore.acquire()

        data = await self._finnhub_driver.get_symbol_data(symbol, resolution)
        await asyncio.sleep(self._waiting_time)
        self._semaphore.release()

        return data

    async def _persist_symbol_resolution_data(self, symbol: str, resolution: str, data):
        if not data:
            return None

        table = await self._timescale_driver.create_symbol_resolution_table(symbol, resolution)
        if table:
            await self._timescale_driver.persist_data_on_tables(data, table)
