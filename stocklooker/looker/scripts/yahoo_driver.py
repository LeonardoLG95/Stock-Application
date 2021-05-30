import asyncio
import json
import re
import time

import aiohttp
from pandas import DataFrame, to_datetime


class YahooDriver:
    def __init__(self, start: int = 0, end: int = int(time.time()), interval: str = '1d', frequency: str = '1d'):
        self.url = "https://finance.yahoo.com/quote/{}/{}"
        self.params = f"history?period1={start}&period2={end}&interval={interval}&frequency={frequency}&filter=history"
        self.session = aiohttp.ClientSession()

    async def fetch_data(self, ticker: str):
        resp = None
        response_okay = False
        url = self.url.format(ticker, self.params)

        try:
            while not response_okay:
                try:
                    response = await self.session.get(url)
                    resp = await response.text()
                    if response.status == 200:
                        response_okay = True
                except:
                    pass
        except Exception as e:
            print(f'Error fetching data {ticker}, error: {e}')
        try:
            pattern = r"root\.App\.main = (.*?);\n}\(this\)\);"
            j = json.loads(re.search(pattern, resp, re.DOTALL).group(1))
            data = j["context"]["dispatcher"]["stores"]["HistoricalPriceStore"]
            prices = DataFrame(data["prices"])
            prices.columns = [col.capitalize() for col in prices.columns]
            prices["Date"] = to_datetime(to_datetime(prices["Date"], unit="s").dt.date)

            if "Data" in prices.columns:
                prices = prices[prices["Data"].isnull()]
            prices = prices[["Date", "High", "Low", "Open", "Close", "Volume", "Adjclose"]]
            prices = prices.rename(columns={"Adjclose": "Adj Close"})

            prices = prices.set_index("Date")
            prices = prices.sort_index().dropna(how="all")

        except Exception as e:
            prices = None
            print(f"No data find it for symbol {ticker} with error: {e}")

        return prices

    async def close_session(self):
        await self.session.close()
