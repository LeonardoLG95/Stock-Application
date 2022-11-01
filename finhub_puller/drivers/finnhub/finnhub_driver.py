import asyncio
import json
import re
from datetime import datetime
from typing import Tuple
from urllib.parse import urlparse

import aiohttp
from json.decoder import JSONDecodeError
from drivers.finnhub.constants import (
    END_POINTS,
    EXPECTED_RESPONSE_KEYS,
    API_TOKEN,
)


class FinnhubDriver:
    def __init__(self, log):
        self.url = END_POINTS["base_url"]
        self.https = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=True)
        )
        self.log = log
        self.number_petitions = 0

        self._waiting_time = 61

        self._semaphore = asyncio.Semaphore(60)

    @staticmethod
    def _parse_url(url: str) -> str:
        return urlparse(url).geturl()

    @staticmethod
    def _now() -> str:
        return str(int(datetime.timestamp(datetime.now())))

    async def _get(self, url: str):
        url = self._parse_url(url)
        await self._semaphore.acquire()

        text = None
        try:
            retry = True
            while retry:
                response = await self.https.get(url)
                if response.status == 200:
                    text = await response.text()
                    retry = False

                elif response.status == 429:
                    self.log.warning(f'To much petitions on : "{url}"')
                    await asyncio.sleep(self._waiting_time)
                    continue

                elif response.status != 200:
                    text = await response.text()
                    try:
                        json_response = json.loads(text)
                    except JSONDecodeError:
                        self.log.error(f'Error status: {response.status}, url: "{url}"')
                        await asyncio.sleep(self._waiting_time)
                        self._semaphore.release()
                        return {}

                    if (
                        json_response
                        and json_response.get("error", "")
                        == "API limit reached. Please try again later. Remaining Limit: 0"
                    ):
                        await asyncio.sleep(self._waiting_time)
                        continue

                    self.log.error(f'Error status: {response.status}, url: "{url}"')
                    retry = False

        finally:
            await asyncio.sleep(self._waiting_time)
            self._semaphore.release()

        if text:
            return json.loads(text)

        self.log.warning(f"No data for url {url}...")
        return {}

    @staticmethod
    def get_index_symbols():
        return END_POINTS["indices"]

    @staticmethod
    def get_resolutions():
        return END_POINTS["resolutions"]

    @staticmethod
    def get_crypto_symbols() -> set:
        return END_POINTS["crypto"]

    async def get_symbols_of_index(self, index_symbol: str) -> set:
        response = await self._get(
            f"{self.url}{END_POINTS['index_endpoint'](index_symbol)}{API_TOKEN}"
        )
        if response:
            return {symbol for symbol in response["constituents"]}

    async def get_symbol_info(self, symbol: str) -> dict:
        info = await self._get(
            f"{self.url}{END_POINTS['stock_info_endpoint'](symbol)}{API_TOKEN}"
        )
        if info and self._check_integrity_keys(
            tuple(info.keys()), EXPECTED_RESPONSE_KEYS["info_keys"]
        ):
            return self._parse_symbol_info(symbol, info)

    def _parse_symbol_info(self, symbol: str, data: dict) -> dict:
        try:
            return {
                "symbol": symbol,
                "name": data["name"],
                "country": data["country"],
                "currency": data["currency"],
                "exchange": data["exchange"],
                "ipo": datetime.strptime(data["ipo"], "%Y-%m-%d"),
                "market_capitalization": data["marketCapitalization"],
                "share_outstanding": data["shareOutstanding"],
                "website": data["weburl"],
                "industry": data["finnhubIndustry"],
            }

        except (KeyError, TypeError):
            self.log.error(f"Wrong info response for symbol: {symbol}")

    async def get_symbol_price(self, symbol, resolution) -> Tuple[dict]:
        price = await self._fetch_symbol_price(symbol, resolution)
        if price and self._check_integrity_keys(
            tuple(price.keys()), EXPECTED_RESPONSE_KEYS["candle_keys"]
        ):
            return self._parse_symbol_price(symbol, resolution, price)

    async def _fetch_symbol_price(self, symbol: str, resolution: str):
        now = self._now()
        return await self._get(
            f"{self.url}{END_POINTS['stock_price_endpoint'](symbol, resolution, now)}{API_TOKEN}"
        )

    def _parse_symbol_price(
        self, symbol: str, resolution: str, price: dict
    ) -> Tuple[dict]:
        parsed_prices = ()
        try:
            for i in range(len(price[EXPECTED_RESPONSE_KEYS["candle_keys"][0]])):
                parsed_prices += (
                    {
                        "time": datetime.fromtimestamp(price["t"][i]),
                        "symbol": symbol,
                        "resolution": resolution,
                        "close": price["c"][i],
                        "high": price["h"][i],
                        "low": price["l"][i],
                        "macd": price["macd"][i],
                        "macd_hist": price["macdHist"][i],
                        "macd_signal": price["macdSignal"][i],
                        "open": price["o"][i],
                        "volume": price["v"][i],
                    },
                )

            return parsed_prices

        except KeyError:
            self.log.error(f"Wrong price response for symbol: {symbol}")

    async def get_basic_financials(self, symbol: str) -> Tuple[dict]:
        basic_financials = await self._get(
            f"{self.url}{END_POINTS['stock_basic_financials'](symbol)}{API_TOKEN}"
        )
        if basic_financials.get("series"):
            return self._parse_basic_financials(symbol, basic_financials["series"])

    def _parse_basic_financials(self, symbol: str, financials: dict) -> Tuple[dict]:
        try:
            return tuple(
                self._parse_financial_time_window(
                    symbol, financials[time_window], time_window
                )
                for time_window in ("quarterly", "annual")
            )

        except KeyError:
            self.log.error(f"Wrong basic financials response for symbol: {symbol}")

    def _parse_financial_time_window(
        self, symbol: str, financials: dict, time_window: str
    ) -> dict:
        longest_column = None
        len_value = 0
        for column in financials:
            longest_column = (
                column if len(financials[column]) > len_value else longest_column
            )
            len_value = (
                len(financials[column])
                if len(financials[column]) > len_value
                else len_value
            )

        row_longest_column = self._camel_to_snake(longest_column)
        row = {}
        for value in financials[longest_column]:
            period = value["period"]
            row = {
                "period": datetime.strptime(period, "%Y-%m-%d"),
                "symbol": symbol,
                "time_window": time_window,
                row_longest_column: value["v"],
            }

            for column in financials:
                if column == longest_column:
                    continue

                for values in financials[column]:
                    if period == values["period"]:
                        row_column = self._camel_to_snake(column)
                        row[row_column] = values["v"]
                        break

        return row

    async def get_financial_report(self, symbol: str, frequency: str):
        reports = await self._get(
            f"{self.url}{END_POINTS['stock_financial_reports'](symbol, frequency)}{API_TOKEN}"
        )

        if reports.get("data") and self._check_integrity_keys(
            tuple(reports["data"][0].keys()), EXPECTED_RESPONSE_KEYS["report_keys"]
        ):
            return self._parse_reports(reports, frequency)

        return None, None

    def _parse_reports(
        self, reports: dict, frequency: str
    ) -> Tuple[Tuple[dict], Tuple[dict]]:
        parsed_reports = ()
        parsed_concepts = ()

        access_numbers = ()
        for report in reports["data"]:
            access_number = report.get("accessNumber")
            if not access_number:
                continue
            id_key = f'{access_number}-{report.get("symbol")}-{frequency}'

            if access_number in access_numbers:
                continue

            parsed_report = self._parse_report(report, id_key, frequency)
            if not parsed_report:
                continue

            access_numbers += (access_number,)
            parsed_reports += (parsed_report,)
            parsed_concepts += self._parse_concepts(report.get("report"), id_key)

        return parsed_reports, parsed_concepts

    def _parse_report(self, report: dict, id_key: str, frequency: str) -> dict:
        parsed_report = {}
        for column, value in report.items():
            if column == "report":
                continue
            if value is None:
                return

            if column in ("startDate", "endDate", "filedDate", "acceptedDate"):
                if value == "":
                    return

                parsed_report[self._camel_to_snake(column)] = datetime.strptime(
                    value, "%Y-%m-%d %H:%M:%S"
                )
            else:
                parsed_report[self._camel_to_snake(column)] = value

        parsed_report["id"] = id_key
        parsed_report["frequency"] = frequency
        return parsed_report

    @staticmethod
    def _parse_concepts(concepts: dict, id_key: str) -> Tuple[dict]:
        if not concepts or not isinstance(concepts, dict):
            return ()

        concepts = {
            json.dumps(concept)
            for raw_concepts in concepts.values()
            for concept in raw_concepts
            if isinstance(concept, dict) and concept.get("value", "") not in ("", "N/A")
        }

        concepts = tuple(json.loads(concept) for concept in concepts)

        parsed_concepts = ()
        for concept in concepts:
            concept["financial_report"] = id_key

            parsed_concepts += (concept,)

        return parsed_concepts

    @staticmethod
    def _check_integrity_keys(keys: tuple, reference_keys: tuple) -> bool:
        for d in reference_keys:
            if d not in keys:
                return False

        return True

    @staticmethod
    def _camel_to_snake(text: str) -> str:
        return re.sub("([A-Z]+)", r"_\1", text).lower()

    async def close(self) -> None:
        await self.https.close()
