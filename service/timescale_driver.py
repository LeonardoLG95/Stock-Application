import asyncio
from datetime import date

import pandas_datareader as web
from pandas import DataFrame

import tecnical_defs as calc


def analyze_stock(data: DataFrame, ticker: str = '?', limit_close: int = 0, limit_rsi: int = 40, limit_macd: int = 1):
    dataset = data

    if dataset is None:
        return
    all_close = dataset['Close'].to_numpy()
    close = all_close[-1]
    if limit_close != 0 and close > limit_close:
        return
    all_low = dataset['Low'].to_numpy()
    stop = calc.get_stop(all_low, 63)
    stop_percent = calc.percent(stop, close)

    all_high = dataset['High'].to_numpy()
    high = calc.get_high(all_high, 63)
    high_percent = calc.percent(high, close)

    if high_percent < -stop_percent:
        return
    rsi = calc.rsi(all_close)

    if rsi > limit_rsi:
        return
    all_macd = calc.macd(all_close)
    macd = all_macd[-1]
    if macd > limit_macd:
        return
    all_signal = calc.ema(all_macd, 9)
    signal = all_signal[len(all_signal) - 1]
    if signal > macd:
        return
    last_date = dataset.index[-1]
    macd_average_h_l = calc.max_macd(all_macd, all_signal)
    macd_low_average = macd_average_h_l[0]
    macd_high_average = macd_average_h_l[1]


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(loop)


def analize_wallet(*wallet):
    wallet_list = sorted(wallet)
    today = date.today()
    today = today.strftime('%Y-%m-%d')
    for ticker in wallet_list:
        dataset = None
        try:
            dataset = web.DataReader(ticker, data_source='yahoo', start='1980-01-01', end=today)
        except Exception as e:
            print(e)
            print('Error al descargar el valor: ', ticker)

        last_date = dataset.index[-1]
        close = dataset['Close'][-1]
        all_close = dataset['Close'].to_numpy()
        all_low = dataset['Low'].to_numpy()
        all_high = dataset['High'].to_numpy()

        rsi = calc.rsi(all_close)
        all_macd = calc.macd(all_close)

        macd = all_macd[len(all_macd) - 1]
        all_signal = calc.ema(all_macd, 9)
        signal = all_signal[len(all_signal) - 1]

        stop = calc.get_stop(all_low, 63)
        stop_percent = calc.percent(stop, close)

        high = calc.get_high(all_high, 63)
        high_percent = calc.percent(high, close)

        macd_average_hl = calc.max_macd(all_macd, all_signal)

        macd_low_average = macd_average_hl[0]
        macd_high_average = macd_average_hl[1]

        if macd < signal:
            ticker += ' ¡MACD HA BAJADO VENDE!'
        else:
            if (rsi >= 70 and (high - close) <= 0) or (rsi >= 70 and macd_high_average <= macd) or (
                    (high - close) <= 0 and macd_high_average <= macd):
                ticker += f' ¡AJUSTA EL STOP a {round(all_close[-2], 2)}!'
