import json
import time
from datetime import datetime
from urllib.parse import urlparse
from typing import List
import aiohttp

from .constants import CONSTANTS
from .finnhub_token import API_TOKEN


class FinnhubDriver:
    def __init__(self, log):
        self.url = CONSTANTS['base_url']
        self.https = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=True))
        self.log = log
        self.number_petitions = 0
        self.candle_keys = ['t', 'c', 'h', 'l', 'macd', 'macdHist', 'macdSignal', 'o', 'v']
        self.info_keys = ['name', 'country', 'currency', 'exchange', 'ipo', 'marketCapitalization', 'shareOutstanding', 'weburl', 'finnhubIndustry']
        self.start_time = time.perf_counter()

    @staticmethod
    def _parse_url(url: str) -> str:
        return urlparse(url).geturl()

    @staticmethod
    def _now() -> str:
        return str(int(datetime.timestamp(datetime.now())))

    async def _get(self, url: str):
        url = self._parse_url(url)

        response = await self.https.get(url)
        return await self._handle_url_response(url, response)

    async def _handle_url_response(self, url, response):
        if response.status == 200:
            text = await response.text()
            data = json.loads(text)
            if data:
                return data

            self.log.warning(f'No data for url {url}...')

        elif response.status == 429:
            self.log.warning(f'To much petitions for url: "{url}"')

        elif response.status != 200:
            self.log.error(f'Error status: {response.status}, url: "{url}"')

        return {}

    @staticmethod
    def get_index_symbols():
        return CONSTANTS['indices']

    @staticmethod
    def get_resolutions():
        return CONSTANTS['resolutions']

    @staticmethod
    def get_crypto_symbols() -> set:
        return CONSTANTS['crypto']

    async def get_symbols_of_index(self, index_symbol: str) -> set:
        response = await self._get(f"{self.url}{CONSTANTS['index_endpoint'](index_symbol)}{API_TOKEN}")

        return {symbol for symbol in response['constituents']}

    async def get_symbol_info(self, symbol: str):
        data = await self._fetch_symbol_info(symbol)
        if data and self._check_integrity_info_keys(list(data.keys())):
            info = (symbol, )
            return info + self._parse_symbol_info(data)
        return ()

    async def _fetch_symbol_info(self, symbol: str):
        data = await self._get(f"{self.url}{CONSTANTS['stock_info_endpoint'](symbol)}{API_TOKEN}")

        return data

    def _check_integrity_info_keys(self, keys: list):
        for d in self.info_keys:
            if d not in keys:
                return False

        return True

    def _parse_symbol_info(self, data: dict) -> tuple:
        info = _handle_key_error(self._info_dict_to_tuple(data))

        # To avoid return a list which is necessary for the price method
        return info if isinstance(info, tuple) else ()

    def _info_dict_to_tuple(self, data: dict) -> tuple:
        parsed_info = ()
        for key in self.info_keys:
            if key == 'ipo':
                parsed_info += (datetime.strptime(data[key], '%Y-%m-%d'),)
                continue

            parsed_info += (data[key],)

        return parsed_info

    async def get_symbol_price(self, symbol, resolution):
        data = await self._fetch_symbol_price(symbol, resolution)
        if data and self._check_integrity_price_keys(list(data.keys())):
            return self._parse_symbol_price(symbol, resolution, data)

        return []

    async def _fetch_symbol_price(self, symbol: str, resolution: str):
        now = self._now()
        data = await self._get(f"{self.url}{CONSTANTS['stock_price_endpoint'](symbol, resolution, now)}{API_TOKEN}")

        return data

    def _check_integrity_price_keys(self, keys: list):
        for d in keys:
            if d != 's' and d not in self.candle_keys:
                return False

        return True

    def _parse_symbol_price(self, symbol: str, resolution: str, data: dict) -> list:
        """
        Parse information for executemany in asyncpg
        :param data: dict result from Finnhub get
        :return: list of candles in tuple format
        """
        return _handle_key_error(
            self._price_dict_to_list_of_tuples(symbol, resolution, data)
        )

    def _price_dict_to_list_of_tuples(self, symbol: str, resolution: str, data: dict) \
            -> List[tuple]:
        parsed_data = []
        for i in range(len(data[self.candle_keys[0]])):
            candle = ()
            for datum_type in self.candle_keys:
                if datum_type == 't':
                    candle += (datetime.fromtimestamp(data[datum_type][i]), symbol, resolution,)
                    continue
                candle += (data[datum_type][i],)

            parsed_data.append(candle)

        return parsed_data

    async def close(self) -> None:
        await self.https.close()


def _handle_key_error(function) -> list:
    try:
        return function
    except KeyError:
        return []
