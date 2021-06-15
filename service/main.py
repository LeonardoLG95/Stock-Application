import time
import tecnical_defs as calc
import asyncio
from yahoo_driver import YahooDriver
from timescale_driver import TimescaleDriver


async def main():
    queue = asyncio.Queue()
    yahoo = YahooDriver()
    ticker_list = yahoo.ticker_list()
    db = TimescaleDriver()
    await db.connect()
    await asyncio.gather(
        *[yahoo.fetch_stocks(ticker, ticker_list[ticker], queue)
          for ticker in ticker_list],
        db.insert_data(queue, len(ticker_list))
    )
    await yahoo.close_session()
    # db.close_connection()


s = time.perf_counter()
asyncio.run(main())
elapsed = time.perf_counter() - s
print(f"{__file__} executed in {elapsed:0.2f} seconds.")

'''def analize_wallet():
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
    macd_high_average = macd_average_hl[1]'''
