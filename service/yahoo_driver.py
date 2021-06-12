import asyncio
import json
import re
import time

import aiohttp
import numpy as np
from pandas import DataFrame, to_datetime
from pytickersymbols import PyTickerSymbols


class YahooDriver:
    def __init__(self, start: int = 0, end: int = int(time.time()), interval: str = '1d', frequency: str = '1d',
                 *markets):
        self.url = "https://finance.yahoo.com/quote/{}/{}"
        self.params = f"history?period1={start}&period2={end}&interval={interval}&frequency={frequency}&filter=history"
        self.session = aiohttp.ClientSession()
        self.markets = ['DOW JONES', 'S&P 500', 'NASDAQ 100']
        if markets:
            self.markets = markets

    async def fetch_stock(self, ticker) -> DataFrame:
        """
        Return individual stock by ticker
        :return: Dataframe with all the stock data
        """
        stock = await self._fetch_data(ticker)
        await self._close_session()
        return self._prepare_data(stock)

    async def fetch_stocks(self) -> list:
        """
        Return all stocks from the markets you instantiate this driver
        :return: a list of all the data from stocks in form of dataframe
        """
        tickers = self._ticker_list()
        stocks = await asyncio.gather(
            self._fetch_data(ticker)
            for ticker in tickers
        )
        await self._close_session()
        stocks_dataframes = []
        for stock in stocks:
            stock_dataframe = self._prepare_data(stock)
            stocks_dataframes.append(stock_dataframe)

        return stocks_dataframes

    def _ticker_list(self) -> list:
        """
        Gives updated list with the names from Yahoo-Finance
        :param markets:
        :return:
        """
        stock_tickers = PyTickerSymbols()
        tickers = []
        for market in self.markets:
            data = stock_tickers.get_stocks_by_index(market)
            data = list(data)
            for stock in data:
                for ticker in stock['symbols']:
                    ticker_label = ticker['yahoo']
                    ticker_validation = re.search(r".*\.F|.*\.L|.*\.R", ticker_label)
                    if not ticker_validation:
                        tickers.append(ticker_label)

        return sorted(np.unique(tickers))

    async def _fetch_data(self, ticker: str) -> str:
        """
        Return all the html without any format
        :param ticker: the identification of the desired stock
        :return: a str, all the html where is the information
        """
        text_response = None
        response_okay = False
        url = self.url.format(ticker, self.params)

        while not response_okay:
            try:
                response = await self.session.get(url)
                if response.status == 200:
                    response_okay = True
                    text_response = await response.text()
                elif response.status == 204:
                    break
                elif response.status == 400:
                    break
            except TimeoutError:
                await asyncio.sleep(0.01)

        return text_response

    def _prepare_data(self, text_response) -> DataFrame:
        """
        Prepare the information from _fetch_data for make it understandable
        :param text_response: all html from Yahoo Finance
        :return: a dataframe with all the data
        """
        pattern = r"root\.App\.main = (.*?);\n}\(this\)\);"
        j = json.loads(re.search(pattern, text_response, re.DOTALL).group(1))
        data = j["context"]["dispatcher"]["stores"]["HistoricalPriceStore"]
        prices = DataFrame(data["prices"])
        prices.columns = [col.capitalize() for col in prices.columns]
        prices["Date"] = to_datetime(to_datetime(prices["Date"], unit="s").dt.date)

        if "Data" in prices.columns:
            prices = prices[prices["Data"].isnull()]

        prices = prices[["Date", "High", "Low", "Open", "Close", "Volume", "Adjclose"]]
        prices = prices.rename(columns={"Adjclose": "Adj Close"})
        prices = prices.set_index("Date")

        return prices.sort_index().dropna(how="all")

    async def _close_session(self):
        await self.session.close()
