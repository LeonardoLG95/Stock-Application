import re
from datetime import datetime

import asyncpg


class TimescaleDriver:
    def __init__(self, db: str = 'stock', user: str = 'postgres', password: str = 'password1234',
                 host: str = '127.0.0.1', port: str = '5500'):
        self.dsn = f'postgres://{user}:{password}@{host}:{port}/{db}'

    async def insert_data(self, stock_information: dict):
        ticker = list(stock_information.keys())[0]
        name = stock_information[ticker]['name']
        stock = stock_information[ticker]['data']
        date = stock.index.to_numpy()
        date = [re.sub(r'T00:00:00\.000000000$', ' 00:00:00+00', str(d)) for d in list(date)]
        date = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S+00') for d in date]
        # open = stock['Open'].to_numpy()
        close = stock['Close'].to_numpy()
        # high = stock['High'].to_numpy()
        low = stock['Low'].to_numpy()
        high = stock['High'].to_numpy()

        stock_data = [
            (datetime.date(date[i]), datetime.date(date[i]),
             ticker, name, 'x', close[i], low[i], high[i], 0, 0, 0)
            for i in range(len(date))
        ]

        con = await asyncpg.connect(dsn=self.dsn)
        await con.executemany('''INSERT INTO looker_stockdata(insert_date, date, yahoo_ticker, name, market, 
                value, low, high, macd_12_26, signal_12_26, rsi_14) VALUES ($1, $2, $3, 
                $4, $5, $6, $7, $8, $9, $10, $11);
            ''', stock_data)
