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
        *[yahoo.fetch_stock(ticker, ticker_list[ticker], queue)
          for ticker in ticker_list],
        db.insert_data(queue, len(ticker_list))
    )
    await yahoo.close_session()
    # db.close_connection()


s = time.perf_counter()
asyncio.run(main())
elapsed = time.perf_counter() - s
print(f"{__file__} executed in {elapsed:0.2f} seconds.")
