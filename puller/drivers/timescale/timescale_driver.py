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
                symbol VARCHAR(30) NOT NULL,
                resolution CHAR NOT NULL,
                close REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                macd REAL NOT NULL,
                macd_hist REAL NOT NULL,
                macd_signal REAL NOT NULL,
                open REAL NOT NULL,
                volume BIGSERIAL NOT NULL,
                PRIMARY KEY(symbol, resolution)
            );
            COMMIT;
        """)
        await con.close()

    async def create_stock_info_table(self):
        con = await self._get_pool()
        await con.execute(f"""
                    BEGIN;
                    CREATE TABLE IF NOT EXISTS stock_info(
                        symbol VARCHAR(30) NOT NULL PRIMARY KEY,
                        name VARCHAR(200) NOT NULL,
                        country VARCHAR(200) NOT NULL,
                        currency VARCHAR(50) NOT NULL,
                        exchange VARCHAR(200) NOT NULL,
                        ipo TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                        market_capitalization BIGSERIAL NOT NULL,
                        share_outstanding REAL NOT NULL,
                        website VARCHAR(200) NOT NULL,
                        industry VARCHAR(200) NOT NULL
                    );
                    COMMIT;
                """)

        await con.close()

    async def create_stock_price_table(self):
        con = await self._get_pool()
        await con.execute(f"""
            BEGIN;
            CREATE TABLE IF NOT EXISTS stock_price(
                time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                symbol VARCHAR(30) NOT NULL,
                resolution CHAR NOT NULL,
                close REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                macd REAL NOT NULL,
                macd_hist REAL NOT NULL,
                macd_signal REAL NOT NULL,
                open REAL NOT NULL,
                volume BIGSERIAL NOT NULL,
                PRIMARY KEY(time, symbol, resolution)
            );
            SELECT create_hypertable('stock_price','time', if_not_exists => TRUE);
            COMMIT;
        """)
        await con.close()

    async def persist_info_data(self, data):
        con = await self._get_pool()
        self.log.info(f'persisting info of {data[1]}...')
        async with con.transaction():
            await con.execute("""
                        INSERT INTO stock_info(symbol, name, country, currency, exchange, ipo, 
                        market_capitalization, share_outstanding, website, industry) 
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) 
                        ON CONFLICT (symbol) DO UPDATE SET (name, country, currency, exchange, ipo, 
                        market_capitalization, share_outstanding, website, industry) = 
                        (EXCLUDED.name, EXCLUDED.country, EXCLUDED.currency, EXCLUDED.exchange, EXCLUDED.ipo, 
                        EXCLUDED.market_capitalization, EXCLUDED.share_outstanding, EXCLUDED.website, EXCLUDED.industry);
                    """, *data)

        await con.close()

    async def persist_price_data(self, data: list) -> None:
        con = await self._get_pool()
        self.log.info(f'persisting data from {data[0][1]} in resolution {data[0][2]}...')
        async with con.transaction():
            await con.executemany(f"""
                INSERT INTO stock_price(time, symbol, resolution, close, high, low, 
                macd, macd_hist, macd_signal, open, volume) 
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) 
                ON CONFLICT (time, symbol, resolution) DO UPDATE SET (close, high, low, 
                macd, macd_hist, macd_signal, open, volume) = 
                (EXCLUDED.close, EXCLUDED.high, EXCLUDED.low, 
                EXCLUDED.macd, EXCLUDED.macd_hist, EXCLUDED.macd_signal, 
                EXCLUDED.open, EXCLUDED.volume);
            """, data)

            await con.execute("""
                INSERT INTO last_candle(time, symbol, resolution, close, high, low, 
                macd, macd_hist, macd_signal, open, volume) 
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) 
                ON CONFLICT (symbol, resolution) DO UPDATE SET (time, close, high, low, 
                macd, macd_hist, macd_signal, open, volume) = 
                (EXCLUDED.time, EXCLUDED.close, EXCLUDED.high, EXCLUDED.low, 
                EXCLUDED.macd, EXCLUDED.macd_hist, EXCLUDED.macd_signal, 
                EXCLUDED.open, EXCLUDED.volume);
            """, *data[len(data)-1])

        await con.close()

    async def _get_pool(self):
        while True:
            try:
                return await self.pool.acquire()
            except asyncio.TimeoutError as e:
                self.log.error(e)

            await asyncio.sleep(0.2)
