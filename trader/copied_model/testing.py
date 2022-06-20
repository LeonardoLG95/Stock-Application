import asyncio

import pandas as pd

from trader.copied_model.rnn import rnn_model
from trader.drivers.timescale.timescale_driver import TimescaleDriver

'''
id = Column(BigInteger, nullable=False, autoincrement=True, primary_key=True)
time = Column(DateTime(timezone=False), nullable=False)
symbol = Column(String, ForeignKey("symbol.symbol"), nullable=False)
resolution = Column(CHAR, nullable=False)
close = Column(Float, nullable=False)
high = Column(Float, nullable=False)
low = Column(Float, nullable=False)
macd = Column(Float, nullable=False)
macd_hist = Column(Float, nullable=False)
macd_signal = Column(Float, nullable=False)
open = Column(Float, nullable=False)
volume = Column(BigInteger, nullable=False)
'''


async def get_stock(symbol: str):
    ts = TimescaleDriver()
    prices = await ts.select_prices(symbol, 'D')
    data = {}

    stop = len(prices) -5
    for i, price in enumerate(prices, 1):
        data.update(
            {
                pd.Timestamp(price.time): {
                    "Open": price.open,
                    "High": price.high,
                    "Low": price.low,
                    "Close": price.close,
                    "AdjClose": price.close,
                    "Volume": price.volume,
                    "date_id": i,
                    "OC_High": price.high,
                    "OC_Low": price.low
                }
            }
        )
        if i >= stop:
            break

    n_candles = len(data)
    stock_data = pd.DataFrame.from_dict(
        data=data,
        orient="index",
    )

    (
        forecast_data_df,
        preds,
        y_valid,
        y_dates_valid,
        scaler,
    ) = rnn_model(data=stock_data["AdjClose"],
                  n_input=40,
                  n_predict=5,
                  learning_rate=0.001,
                  epochs=500,
                  batch_size=None,
                  test_size=0.5,
                  n_loops=1,
                  no_shuffle=True)
    print(symbol)
    print(forecast_data_df[0])

    '''
    prediction = rnn_model(data=stock_data,
                           n_input=40,
                           n_predict=5,
                           learning_rate=0.1,
                           epochs=50,
                           batch_size=None,
                           test_size=0.5,
                           n_loops=1,
                           no_shuffle=True)
    forecast_data_df.median(axis=1)
    forecast_data_df["Median"]
    forecast_data_df[0]
    '''


asyncio.run(get_stock('CPB'))
