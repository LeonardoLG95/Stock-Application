import asyncio
import time

import ticker_symbols as ts
from timescale_driver import TimescaleDriver
from yahoo_driver import YahooDriver


async def main():
    ticker_list = ts.yahoo_ticker_list()
    info_queue = asyncio.Queue()
    data_queue = asyncio.Queue()
    yahoo = YahooDriver()
    db = TimescaleDriver()
    await db.connect()
    '''
    1) put(info_queue) last time updated -> 
    2) get(info_queue) for fetch data and put(data_queue) data -> 
    3) get(data_queue) for insert
    '''
    await asyncio.gather(
        *[db.last_time_updated(ticker, ticker_list[ticker], info_queue)
          for ticker in ticker_list],
        *[yahoo.fetch_stock(info_queue, data_queue)
          for _ in ticker_list],
        *[db.insert_data(data_queue)
          for _ in ticker_list]
    )
    await yahoo.close()


s = time.perf_counter()
asyncio.run(main())
elapsed = time.perf_counter() - s
print(f"{__file__} executed in {elapsed:0.2f} seconds.")
