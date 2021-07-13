import asyncio
import json
import re
import time

from aiohttp import client_exceptions
import aiohttp

from pandas import DataFrame, to_datetime
from datetime import datetime, date


class YahooDriver:
    def __init__(self):
        self.url = "https://finance.yahoo.com/quote/{}/{}"
        self.params = f"history?period1=0&period2={int(time.time())}&interval=1d&frequency=1d&filter=history"
        self.headers = {
            "Connection": "keep-alive",
            "Expires": str(-1),
            "Upgrade-Insecure-Requests": str(1),
            # Google Chrome:
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"
            ),
        }
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), headers=self.headers)

    async def fetch_stock(self, info_queue: asyncio.Queue, data_queue: asyncio.Queue) -> None:
        """
        Return a dict with stock data or empty (in case don't find it) in a async queue.
        :param info_queue: a queue where the information of the stock is stored
        :param data_queue: a queue where the result(info + dataframe) will be stored
        :return: the data from a stock in data_queue
        """
        info = await info_queue.get()

        if not info:
            return None

        ticker = info.get('ticker')
        name = info.get('name')
        last_time = info.get('last_time')

        if last_time:
            self._set_interval(last_time)

        response_html = None
        response_okay = False
        url = self.url.format(ticker, self.params)
        while not response_okay:
            try:
                response = await self.session.get(url)
                if response.status == 200:
                    try:
                        response_html = await response.text()
                    except(ConnectionAbortedError, client_exceptions.ServerDisconnectedError,
                           TimeoutError, asyncio.TimeoutError, client_exceptions.ClientOSError):
                        continue
                    response_okay = True

                elif response.status != 200:
                    print(f'Bad status : {name}, ticker : {ticker}')
                    continue
                else:
                    break
            except (ConnectionAbortedError, client_exceptions.ServerDisconnectedError,
                    TimeoutError, asyncio.TimeoutError, client_exceptions.ClientOSError):
                continue

        if not response_html:
            print(f'Failed to download, no html in response : {name}, ticker : {ticker}')
            await data_queue.put({})
            return None

        dataframe = self._prepare_data(response_html)
        if dataframe.empty:
            await data_queue.put({})
            print(f'Failed to download, dataframe empty : {name}, ticker : {ticker}')
            return None

        info['data'] = dataframe
        # print(info)
        await data_queue.put(info)

        # print(f'Downloaded : {name}, ticker : {ticker}')

    async def close(self) -> None:
        """
        Close connection of the driver
        :return: none
        """
        await self.session.close()

    def _set_interval(self, start: date) -> None:
        """
        Sets the start time value in the params of the petition
        :param start: start time from where you want to make the petition (inclusive "CHECK")
        :return: none
        """
        if not start:
            raise NotImplementedError('set_interval called without start')

        self.params = f"history?period1={int(time.mktime(datetime.strptime(str(start), '%Y-%m-%d').timetuple()))}" \
                      f"&period2={int(time.time())}" \
                      f"&interval=1d&frequency=1d&filter=history"

    def _prepare_data(self, html: str) -> DataFrame:
        """
        Prepare information from fetch_stock for make it readable
        :param html: all html from Yahoo Finance fetch
        :return: a dataframe with all the data
        """
        try:
            pattern = r"root\.App\.main = (.*?);\n}\(this\)\);"
            j = json.loads(re.search(pattern, html, re.DOTALL).group(1))
            data = j["context"]["dispatcher"]["stores"]["HistoricalPriceStore"]
        except KeyError:
            return DataFrame(None)

        if not data.get("prices"):
            return DataFrame(None)
        prices = DataFrame(data["prices"])
        prices.columns = [col.capitalize() for col in prices.columns]
        prices["Date"] = to_datetime(to_datetime(prices["Date"], unit="s").dt.date)

        if "Data" in prices.columns:
            prices = prices[prices["Data"].isnull()]

        prices = prices[["Date", "High", "Low", "Open", "Close", "Volume", "Adjclose"]]
        prices = prices.set_index("Date")

        return prices.sort_index().dropna(how="all")
