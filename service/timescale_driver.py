import re
from datetime import datetime

import asyncio
import asyncpg


class TimescaleDriver:
    def __init__(self, db: str = 'stock', user: str = 'postgres', password: str = 'password1234',
                 host: str = '127.0.0.1', port: str = '5500'):
        self.dsn = f'postgres://{user}:{password}@{host}:{port}/{db}'
        self.con = None

    async def connect(self):
        self.con = await asyncpg.connect(dsn=self.dsn)

    async def insert_data(self, queue: asyncio.Queue, stock_count: int):
        for _ in range(stock_count):
            stock_information = await queue.get()
            if not stock_information:
                continue
            ticker = list(stock_information.keys())[0]
            name = stock_information[ticker]['name']
            stock = stock_information[ticker]['data']
            date = stock.index.to_numpy()
            date = [re.sub(r'T00:00:00\.000000000$', ' 00:00:00+00', str(d)) for d in list(date)]
            date = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S+00') for d in date]
            close = stock['Close'].to_numpy()
            low = stock['Low'].to_numpy()
            high = stock['High'].to_numpy()
            open_values = stock['Open'].to_numpy()
            volume = stock['Volume'].to_numpy()

            stock_data = [
                (f'{datetime.date(date[i])}-{ticker}', datetime.date(date[i]),
                 ticker, name, close[i], low[i], high[i], 0, 0, 0, open_values[i], volume[i])
                for i in range(len(date))
            ]

            if self.con:
                await self.con.executemany('''INSERT INTO looker_stockdata_to_django(id, date, yahoo_ticker, name, 
                        close, low, high, macd_12_26, signal_12_26, rsi_14, open, volume) VALUES ($1, $2, $3, 
                        $4, $5, $6, $7, $8, $9, $10, $11, $12) ON CONFLICT (id) DO UPDATE SET (date, yahoo_ticker, name, 
                        close, low, high, macd_12_26, signal_12_26, rsi_14, open, volume) = (EXCLUDED.date, 
                        EXCLUDED.yahoo_ticker, EXCLUDED.name, EXCLUDED.close, EXCLUDED.low, EXCLUDED.high, 
                        EXCLUDED.macd_12_26, EXCLUDED.signal_12_26, EXCLUDED.rsi_14, EXCLUDED.open, EXCLUDED.volume); 
                    ''', stock_data)
                print(f'Inserted : {name}')
            else:
                raise Exception('Connection not created please call first the method connect from this driver!')
