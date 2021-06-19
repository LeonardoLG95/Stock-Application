import asyncio
import json
import re
import time

from aiohttp import client_exceptions
import aiohttp

from pandas import DataFrame, to_datetime
from pytickersymbols import PyTickerSymbols


class YahooDriver:
    def __init__(self, start: int = 0, end: int = int(time.time()), interval: str = '1d', frequency: str = '1d',
                 *markets):
        self.url = "https://finance.yahoo.com/quote/{}/{}"
        self.params = f"history?period1={start}&period2={end}&interval={interval}&frequency={frequency}&filter=history"
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))
        self.markets = ['DOW JONES', 'S&P 500', 'NASDAQ 100']
        if markets:
            self.markets = markets

    def ticker_list(self) -> list:
        """
        Gives updated list with the tickers of index stocks for Yahoo-Finance
        :return: a list with all the tickers
        """
        stock_tickers = PyTickerSymbols()
        tickers = {}
        for market in self.markets:
            data = stock_tickers.get_stocks_by_index(market)
            data = list(data)
            for stock in data:
                for ticker in stock['symbols']:
                    ticker_label = ticker['yahoo']
                    ticker_validation = re.search(r".*\.F|.*\.L|.*\.R", ticker_label)
                    if ticker_validation:
                        continue
                    name = stock.get('name')
                    tickers[ticker_label] = name

        return tickers

    async def fetch_stock(self, ticker: str, name: str, queue: asyncio.Queue) -> None:
        """
        Return a dict with stock data or empty (in case don't find it) in a async queue.
        :param ticker: the identification of the desired stock
        :param name: the name of the desired stock
        :param queue: a queue where the result will be stored
        :return: a str, all the html where is the information
        """
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
                    break
                else:
                    continue
            except (ConnectionAbortedError, client_exceptions.ServerDisconnectedError,
                    TimeoutError, asyncio.TimeoutError, client_exceptions.ClientOSError):
                continue

        if not response_html:
            await queue.put({})
            return None
        dataframe = self._prepare_data(response_html)
        if dataframe.empty:
            await queue.put({})
            return None

        await queue.put({
            ticker: {
                'name': name,
                'data': dataframe
            }
        })
        print(f'Downloaded : {name}, ticker {ticker}')

    async def close_session(self):
        """
        Close connection of the driver
        """
        await self.session.close()

    def _prepare_data(self, html: str) -> DataFrame:
        """
        Prepare information from _fetch_data for make it readable
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
