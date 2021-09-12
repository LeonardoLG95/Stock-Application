import asyncio
import time

from service.utilities import ticker_symbols as ts
from service.drivers.timescale_driver import TimescaleDriver
from service.drivers.yahoo_driver import YahooDriver
from datetime import datetime, timedelta


async def main() -> None:
    """
    Main function of the service
    :return: none
    """
    s = time.perf_counter()

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

    elapsed = time.perf_counter() - s
    print(f"Service function executed in : \t{elapsed:0.2f} seconds.")
    await asyncio.sleep(60)


asyncio.run(main())
while True:
    now = datetime.now()

    now_weekday = now.weekday()
    day_now = now.day
    month_now = now.month
    year_now = now.year

    # spain time
    open_time = datetime(year_now, month_now, day_now, 15, 0, 0)
    # 15 min extra for update with the final information of the day
    close_time = datetime(year_now, month_now, day_now, 22, 15, 0)

    if now_weekday < 5 and open_time <= now < close_time:
        asyncio.run(main())
    else:
        # for sleep the service until open
        now_timestamp = now.timestamp()
        if now_weekday < 5:
            # weekdays
            if open_time > now:
                open_time = open_time.timestamp()
                wait = open_time - now_timestamp
            elif now.weekday() != 4 and now > close_time:
                next_day = open_time + timedelta(days=1)
                next_day = next_day.timestamp()
                wait = next_day - now_timestamp
            else:
                monday_open = open_time + timedelta(days=3)
                monday_open = monday_open.timestamp()
                wait = monday_open - now_timestamp
        else:
            # weekend
            days_until_monday = 7 - now_weekday
            monday_open = open_time + timedelta(days=days_until_monday)
            monday_open = monday_open.timestamp()
            wait = monday_open - now_timestamp

        print(f'Sleep for {wait} seconds')
        time.sleep(wait)
