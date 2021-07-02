import re
from datetime import datetime, timedelta, timezone
import tecnical_defs as calc
import asyncio
import asyncpg
import numpy as np


class TimescaleDriver:
    def __init__(self, db: str = 'stock', user: str = 'postgres', password: str = 'password1234',
                 host: str = '127.0.0.1', port: str = '5500'):
        self.dsn = f'postgres://{user}:{password}@{host}:{port}/{db}'
        self.pool = None

    async def connect(self):
        """
        Start connection, create pool for all the queries
        """
        self.pool = await asyncpg.create_pool(dsn=self.dsn)

    async def last_time_updated(self, ticker: str, name: str, queue: asyncio.Queue) -> None:
        """
        Take last insert date for a ticker.
        :param ticker: ticker of the desired stock
        :param name: name of the bussiness
        :param queue: where the result is stored
        :return:
        """
        con = await self._connect()
        insert_date = await con.fetchval('''SELECT insert_date FROM looker_stockdata_to_django 
                                        WHERE yahoo_ticker=($1) ORDER BY date DESC LIMIT 1;''', ticker)
        await con.close()

        if not insert_date:
            await queue.put({'ticker': ticker,
                             'name': name,
                             'last_time': None
                             })
            return None

        insert_date += timedelta(hours=2)
        year = insert_date.year
        month = insert_date.month
        day = insert_date.day

        close_date = datetime(year, month, day, 22, 1, 0, tzinfo=timezone.utc)

        # If was updated before close, recover that day
        if insert_date < close_date:
            await queue.put({'ticker': ticker,
                             'name': name,
                             'last_time': datetime(year, month, day, tzinfo=timezone.utc)
                             })
            return None

        # If was updated after close, recover since next
        await queue.put({'ticker': ticker,
                         'name': name,
                         'last_time': datetime(year, month, day + 1, tzinfo=timezone.utc)
                         })

    async def insert_data(self, queue: asyncio.Queue) -> None:
        """
        It pulls data from the queue, processes it (this will probably be separated in the future)
        and stores it in the database.
        :param queue: where the data is stored
        :return: none
        """
        stock_information = await queue.get()
        if not stock_information:
            return None

        ticker = stock_information.get('ticker')
        name = stock_information.get('name')
        stock = stock_information.get('data')
        last_time = stock_information.get('last_time')

        date = stock.index.to_numpy()
        date = [re.sub(r'T00:00:00\.000000000$', ' 00:00:00+00', str(d)) for d in list(date)]
        date = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S+00') for d in date]
        close = stock['Close'].to_numpy()
        close_for_calc = close
        low = stock['Low'].to_numpy()
        high = stock['High'].to_numpy()
        open_values = stock['Open'].to_numpy()
        volume = stock['Volume'].to_numpy()

        con = await self._connect()
        if last_time:
            all_close = await con.fetch('''SELECT close FROM looker_stockdata_to_django 
                                                        WHERE yahoo_ticker=($1) ORDER BY date ASC;''', ticker)
            close_for_calc = np.array([])
            for price in all_close:
                close_for_calc = np.append(close_for_calc, price.get('close'))
            close_for_calc = np.append(close_for_calc, close)

        macd = calc.macd(close_for_calc)
        signal = calc.ema(macd, 9)
        rsi = calc.rsi(close_for_calc)

        if not last_time:
            macd_12_26 = np.insert(macd, 0, [np.NaN for _ in range(25)], axis=0)
            signal_12_26 = np.insert(signal, 0, [np.NaN for _ in range(33)], axis=0)
            rsi_14 = np.insert(rsi, 0, [np.NaN for _ in range(14)], axis=0)
        else:
            count_prices = len(close)
            macd_12_26 = macd[-count_prices:]
            signal_12_26 = signal[-count_prices:]
            rsi_14 = rsi[-count_prices:]

        stock_data = [
            (f'{datetime.date(date[i])}-{ticker}', datetime.date(date[i]),
             ticker, close[i], low[i], high[i], macd_12_26[i],
             signal_12_26[i], rsi_14[i], open_values[i], volume[i])
            for i in range(len(date))
        ]

        await con.executemany('''INSERT INTO looker_stockdata_to_django(id, date, yahoo_ticker, 
                close, low, high, macd_12_26, signal_12_26, rsi_14, open, volume) VALUES ($1, $2, $3, 
                $4, $5, $6, $7, $8, $9, $10, $11) ON CONFLICT (id) DO UPDATE SET (date, yahoo_ticker, 
                close, low, high, macd_12_26, signal_12_26, rsi_14, open, volume) = (EXCLUDED.date, 
                EXCLUDED.yahoo_ticker, EXCLUDED.close, EXCLUDED.low, EXCLUDED.high, 
                EXCLUDED.macd_12_26, EXCLUDED.signal_12_26, EXCLUDED.rsi_14, EXCLUDED.open, EXCLUDED.volume);'''
                              , stock_data)
        fetch_name = await con.fetchval('''SELECT name FROM stock_names WHERE ticker=($1);''', ticker)
        if not fetch_name:
            await con.execute('''INSERT INTO stock_names(ticker, name) VALUES ($1, $2);''', ticker, name)
        await con.close()

        print(f'Inserted : {name}, ticker: {ticker}')

    async def _connect(self):
        """
        Return pool for queries
        :return: pool.acquire()
        """
        con = await self.pool.acquire()
        if not con:
            raise ConnectionError('Connection not created please call first the method connect() from this driver!')

        return con
