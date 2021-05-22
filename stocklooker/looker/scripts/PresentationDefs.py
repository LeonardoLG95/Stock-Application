import pandas_datareader as web
import numpy as np
from datetime import date
from tqdm import tqdm
import TecnicalDefs as calc
from pytickersymbols import PyTickerSymbols
import re


def string_result(ticker: str, last_date, close: float,
                  rsi: float, macd: float,
                  macd_low_average: float,
                  macd_high_average: float,
                  signal: float,
                  stop: float, stop_percent: float,
                  high: float, high_percent: float) -> str:
    '''
    Convert inputs in floats rounded to 2 decimals and
    return a string with all information formated
    :param ticker:
    :param last_date:
    :param close:
    :param rsi:
    :param macd:
    :param macd_low_average:
    :param macd_high_average:
    :param signal:
    :param stop:
    :param stop_percent:
    :param high:
    :param high_percent:
    :return:
    '''

    close = round(close, 2)
    rsi = round(rsi, 2)
    macd = round(macd, 2)
    macd_low_average = round(macd_low_average, 2)
    macd_high_average = round(macd_high_average, 2)
    signal = round(signal, 2)
    stop = round(stop, 2)
    stop_percent = round(stop_percent, 2)
    high = round(high, 2)
    high_percent = round(high_percent, 2)

    string_result = f'----------------{ticker}----------------\n \
Last date = {last_date} | Close = {close}$\n \
RSI = {rsi}\n \
MACD = {macd} | High avg (High) = {macd_high_average} | Low avg (Low) = {macd_low_average}\n \
Signal = {signal}\n\n \
Calculated in 3 months (63 periods):\n \
Stop Loss = {stop}$ | {stop_percent}%\n \
High = {high}$ | {high_percent}%\n'

    return string_result


def ticker_list(*markets: str) -> list:
    '''
    Gives updated list with the names from Yahoo-Finance
    :param markets:
    :return:
    '''

    stock_tickers = PyTickerSymbols()
    tickers = []
    for market in markets:
        data = stock_tickers.get_stocks_by_index(market)
        data = list(data)
        for stock in data:
            for ticker in stock['symbols']:
                ticker_label = ticker['yahoo']
                ticker_validation = re.search(r".*\.F|.*\.L|.*\.R", ticker_label)
                if ticker_validation is None:
                    tickers.append(ticker_label)
    return sorted(np.unique(tickers))


def analize_index(limit_close: int = 0, limit_rsi: int = 40, limit_macd: int = 0) -> print:
    tickers = ticker_list('DOW JONES', 'S&P 500', 'NASDAQ 100')

    today = date.today()
    today = today.strftime('%Y-%m-%d')

    out_str = ''
    dw_str = 'Error al descargar: '
    err_str = 'Error al calcular: '
    for e in tqdm(range(len(tickers)), desc="Analyzing"):
        ticker = tickers[e]
        try:
            try:
                dataset = web.DataReader(ticker, data_source='yahoo', start='1980-01-01', end=today)
            except:
                dw_str += ticker + ' | '

            all_close = dataset['Close'].to_numpy()
            close = all_close[-1]
            if close <= limit_close or limit_close == 0:
                all_low = dataset['Low'].to_numpy()
                stop = calc.calcStop(all_low, 63)
                stop_percent = calc.calcPercent(stop, close)

                all_high = dataset['High'].to_numpy()
                high = calc.calcHigh(all_high, 63)
                high_percent = calc.calcPercent(high, close)

                if high_percent > -stop_percent:
                    rsi = calc.calcRsi(all_close)

                    if rsi < limit_rsi or limit_rsi == 0:
                        all_macd = calc.calcMacd(all_close)
                        macd = all_macd[-1]

                        if macd < limit_macd:
                            allSignal = calc.calcEMA(all_macd, 9)
                            signal = allSignal[len(allSignal) - 1]
                            if signal < macd:
                                last_date = dataset.index[-1]
                                macdAverageHL = calc.calcMaxMacd(all_macd, allSignal)
                                macd_low_average = macdAverageHL[0]
                                macd_high_average = macdAverageHL[1]

                                out_str += string_result(ticker, last_date, close, rsi, macd, macd_low_average,
                                                         macd_high_average, signal, stop, stop_percent, high,
                                                         high_percent)
        except:
            err_str += ticker + ' | '

    if out_str != '':
        print(out_str)
    else:
        print('No hay coincidencias.')
    if err_str != 'Error al calcular: ':
        print(err_str)
    if dw_str != 'Error al descargar: ':
        print(dw_str)


def analize_wallet(*wallet):
    wallet_list = sorted(wallet)

    today = date.today()
    today = today.strftime('%Y-%m-%d')
    for ticker in wallet_list:
        try:
            dataset = web.DataReader(ticker, data_source='yahoo', start='1980-01-01', end=today)
        except:
            print('Error al descargar el valor: ', ticker)

        last_date = dataset.index[-1]
        close = dataset['Close'][-1]
        all_close = dataset['Close'].to_numpy()
        all_low = dataset['Low'].to_numpy()
        all_high = dataset['High'].to_numpy()

        rsi = calc.calcRsi(all_close)
        all_macd = calc.calcMacd(all_close)

        macd = all_macd[len(all_macd) - 1]
        all_signal = calc.calcEMA(all_macd, 9)
        signal = all_signal[len(all_signal) - 1]

        stop = calc.calcStop(all_low, 63)
        stop_percent = calc.calcPercent(stop, close)

        high = calc.calcHigh(all_high, 63)
        high_percent = calc.calcPercent(high, close)

        macd_average_hl = calc.calcMaxMacd(all_macd, all_signal)

        macd_low_average = macd_average_hl[0]
        macd_high_average = macd_average_hl[1]

        if macd < signal:
            ticker += ' ¡MACD HA BAJADO VENDE!'
        else:
            if (rsi >= 70 and (high - close) <= 0) or (rsi >= 70 and macd_high_average <= macd) or (
                    (high - close) <= 0 and macd_high_average <= macd):
                ticker += f' ¡AJUSTA EL STOP a {round(all_close[-2], 2)}!'

        out_str = string_result(ticker, last_date, close, rsi, macd, macd_low_average, macd_high_average, signal, stop,
                                stop_percent, high, high_percent)

        print(out_str)
