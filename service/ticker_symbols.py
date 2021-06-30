"""
For now just take the tickers for yahoo but this 
can be converted into an object for more data sources.
And async version.
"""
from pytickersymbols import PyTickerSymbols
import re


def yahoo_ticker_list() -> dict:
    """
    Gives updated list with the tickers of index stocks for Yahoo-Finance
    :return: a list with all tickers
    """
    ticker_symbols = PyTickerSymbols()
    tickers = {}
    for market in ['DOW JONES', 'S&P 500', 'NASDAQ 100']:
        data = ticker_symbols.get_stocks_by_index(market)
        data = list(data)
        for stock in data:
            for ticker in stock['symbols']:
                ticker_key = ticker['yahoo']
                ticker_validation = re.search(r".*\.F|.*\.L|.*\.R", ticker_key)
                if ticker_validation:
                    continue
                name = stock.get('name')
                tickers[ticker_key] = name

    return tickers
