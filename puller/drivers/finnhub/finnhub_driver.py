import json
import time
from datetime import datetime
from typing import List
from urllib.parse import urlparse

import aiohttp

from stock_utils.models.classes import StockInfo, StockPrice
from .constants import CONSTANTS
from .finnhub_token import API_TOKEN


class FinnhubDriver:
    def __init__(self, log):
        self.url = CONSTANTS['base_url']
        self.https = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=True))
        self.log = log
        self.number_petitions = 0
        self.candle_keys = ['t', 'c', 'h', 'l', 'macd', 'macdHist', 'macdSignal', 'o', 'v']
        self.info_keys = ['name', 'country', 'currency', 'exchange', 'ipo', 'marketCapitalization', 'shareOutstanding',
                          'weburl', 'finnhubIndustry']
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
        info = await self._fetch_symbol_info(symbol)
        if info and self._check_integrity_info_keys(list(info.keys())):
            return self._parse_symbol_info(symbol, info)

        return None

    async def _fetch_symbol_info(self, symbol: str):
        data = await self._get(f"{self.url}{CONSTANTS['stock_info_endpoint'](symbol)}{API_TOKEN}")

        return data

    def _check_integrity_info_keys(self, keys: list):
        for d in self.info_keys:
            if d not in keys:
                return False

        return True

    @staticmethod
    def _parse_symbol_info(symbol: str, data: dict) -> StockInfo:
        try:
            return StockInfo(symbol=symbol, name=data['name'], country=data['country'], currency=data['currency'],
                             exchange=data['exchange'], ipo=datetime.strptime(data['ipo'], '%Y-%m-%d'),
                             market_capitalization=data['marketCapitalization'],
                             share_outstanding=data['shareOutstanding'],
                             website=data['weburl'], industry=data['finnhubIndustry'])
        except (KeyError, TypeError):
            return None

    async def get_symbol_price(self, symbol, resolution):
        data = await self._fetch_symbol_price(symbol, resolution)
        if data and self._check_integrity_price_keys(list(data.keys())):
            return self._parse_symbol_price(symbol, resolution, data)

        return None

    async def _fetch_symbol_price(self, symbol: str, resolution: str):
        now = self._now()
        data = await self._get(f"{self.url}{CONSTANTS['stock_price_endpoint'](symbol, resolution, now)}{API_TOKEN}")

        return data

    def _check_integrity_price_keys(self, keys: list):
        for d in self.candle_keys:
            if d != 's' and d not in keys:
                return False

        return True

    def _parse_symbol_price(self, symbol: str, resolution: str, data: dict) \
            -> List[StockPrice]:
        try:
            parsed_prices = []
            for i in range(len(data[self.candle_keys[0]])):
                parsed_prices.append(
                    StockPrice(
                        time=datetime.fromtimestamp(data['t'][i]),
                        symbol=symbol,
                        resolution=resolution,
                        close=data['c'][i],
                        high=data['h'][i],
                        low=data['l'][i],
                        macd=data['macd'][i],
                        macd_hist=data['macdHist'][i],
                        macd_signal=data['macdSignal'][i],
                        open=data['o'][i],
                        volume=data['v'][i],
                    )
                )

            return parsed_prices

        except KeyError:
            return None

    async def close(self) -> None:
        await self.https.close()
