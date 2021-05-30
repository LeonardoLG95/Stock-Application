import asyncio
import re
from asyncio import AbstractEventLoop

from pandas import DataFrame
from pytickersymbols import PyTickerSymbols

import tecnical_defs as calc
from yahoo_driver import YahooDriver


def ticker_list(*markets: str) -> dict:
    """
    Gives updated list with the names from Yahoo-Finance
    :param markets:
    :return:
    """
    stock_tickers = PyTickerSymbols()
    tickers = {}
    for market in markets:
        data = stock_tickers.get_stocks_by_index(market)
        data = list(data)
        for stock in data:
            name = stock['name']
            for ticker in stock['symbols']:
                ticker_label = ticker['yahoo']
                ticker_validation = re.search(r".*\.F|.*\.L|.*\.R", ticker_label)
                if ticker_validation is None:
                    tickers[name] = ticker_label
                    break

    return tickers


def insert_information(dataset: DataFrame, ticker: str, name: str):
    if dataset is not None:
        analyzed = False
        all_close = dataset['Close'].to_numpy()
        close = all_close[-1]

        # low and high, and his percentages
        # low
        all_low = dataset['Low'].to_numpy()
        stop = calc.get_stop(all_low, 63)
        stop_percent = calc.percent(stop, close)
        # high
        all_high = dataset['High'].to_numpy()
        high = calc.get_high(all_high, 63)
        high_percent = calc.percent(high, close)
        # rsi
        rsi = calc.rsi(all_close)
        # macd
        all_macd = calc.macd(all_close)
        macd = all_macd[-1]
        # signal
        all_signal = calc.ema(all_macd, 9)
        signal = all_signal[len(all_signal) - 1]
        # last date
        last_date = dataset.index[-1]

        macd_average_h_l = calc.max_macd(all_macd, all_signal)
        macd_low_average = macd_average_h_l[0]
        macd_high_average = macd_average_h_l[1]


async def update_stocks(loop: AbstractEventLoop):
    con = YahooDriver()
    tickers = ticker_list('DOW JONES', 'S&P 500', 'NASDAQ 100')
    tasks = []
    for name in tickers:
        # pass the function, the ticker and the business name (dict)
        tasks.append((loop.create_task(con.fetch_data(tickers[name])), tickers[name], name))

    for task, ticker, name in tasks:
        data = await task
        insert_information(data, ticker, name)

    await con.close_session()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_stocks(loop))
