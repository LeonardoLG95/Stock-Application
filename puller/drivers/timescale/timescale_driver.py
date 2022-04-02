import asyncio

import asyncpg



class TimescaleDriver:
    def __init__(self, log, user: str = 'postgres', password: str = 'password1234',
                 host: str = 'localhost', port: str = '5500', db: str = 'stock'):
        self.dsn = f'postgres://{user}:{password}@{host}:{port}/{db}'
        self.log = log
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn)

    async def create_last_candle_table(self):
        con = await self._get_pool()
        await con.execute("""
            BEGIN;
            CREATE TABLE IF NOT EXISTS last_candle(
                time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                table_name VARCHAR(50) NOT NULL PRIMARY KEY,
                close REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                macd REAL NOT NULL,
                macd_hist REAL NOT NULL,
                macd_signal REAL NOT NULL,
                open REAL NOT NULL,
                volume BIGSERIAL NOT NULL
            );
            COMMIT;
        """)
        await con.close()

    async def create_symbol_resolution_table(self, symbol, resolution):
        if '.' in symbol:
            symbol = symbol.replace('.', '_')
        if '-' in symbol:
            symbol = symbol.replace('-', '_')
        if ':' in symbol:
            symbol = symbol.replace(':', '_')

        table = f'{symbol}_{resolution}'
        con = await self._get_pool()
        await con.execute(f"""
            BEGIN;
            CREATE TABLE IF NOT EXISTS {table}(
                time TIMESTAMP WITHOUT TIME ZONE NOT NULL primary key,
                close REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                macd REAL NOT NULL,
                macd_hist REAL NOT NULL,
                macd_signal REAL NOT NULL,
                open REAL NOT NULL,
                volume BIGSERIAL NOT NULL
            );
            SELECT create_hypertable('{table}','time', if_not_exists => TRUE);
            COMMIT;
        """)
        await con.close()

        return table

    async def persist_data_on_tables(self, data: list, table: str) -> None:
        con = await self._get_pool()
        self.log.error(f'persisting data in table {table}...')
        async with con.transaction():
            await con.executemany(f"""
                INSERT INTO {table}(time, close, high, low, 
                macd, macd_hist, macd_signal, open, volume) 
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) 
                ON CONFLICT (time) DO UPDATE SET (close, high, low, 
                macd, macd_hist, macd_signal, open, volume) = 
                (EXCLUDED.close, EXCLUDED.high, EXCLUDED.low, 
                EXCLUDED.macd, EXCLUDED.macd_hist, EXCLUDED.macd_signal, 
                EXCLUDED.open, EXCLUDED.volume);
            """, data)

            await con.execute("""
                INSERT INTO last_candle(time, table_name, close, high, low, 
                macd, macd_hist, macd_signal, open, volume) 
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) 
                ON CONFLICT (table_name) DO UPDATE SET (time, close, high, low, 
                macd, macd_hist, macd_signal, open, volume) = 
                (EXCLUDED.time, EXCLUDED.close, EXCLUDED.high, EXCLUDED.low, 
                EXCLUDED.macd, EXCLUDED.macd_hist, EXCLUDED.macd_signal, 
                EXCLUDED.open, EXCLUDED.volume);
            """, *data[len(data)-1][:1] + (table,) + data[len(data)-1][1:])

        await con.close()

    async def _get_pool(self):
        while True:
            try:
                return await self.pool.acquire()
            except asyncio.TimeoutError as e:
                self.log.error(e)

            await asyncio.sleep(0.2)
