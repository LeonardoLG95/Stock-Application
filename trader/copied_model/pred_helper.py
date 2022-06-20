from datetime import datetime, timedelta
from typing import List, Union

import numpy as np
import pandas as pd
from holidays import US as us_holidays
from keras.models import Sequential
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from config_neural_network_models import PREPROCESS


def prepare_scale_train_valid_test(
        data: Union[pd.DataFrame, pd.Series],
        n_input_days: int,
        n_predict_days: int,
        test_size: float,
        s_end_date: str,
        no_shuffle: bool,
):
    """
    Prepare and scale train, validate and test data.
    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of stock prices
    ns_parser: argparse.Namespace
        Parsed arguments
    Returns
    -------
    X_train: np.ndarray
        Array of training data.  Shape (# samples, n_inputs, 1)
    X_test: np.ndarray
        Array of validation data.  Shape (total sequences - #samples, n_inputs, 1)
    y_train: np.ndarray
        Array of training outputs.  Shape (#samples, n_days)
    y_test: np.ndarray
        Array of validation outputs.  Shape (total sequences -#samples, n_days)
    X_dates_train: np.ndarray
        Array of dates for X_train
    X_dates_test: np.ndarray
        Array of dates for X_test
    y_dates_train: np.ndarray
        Array of dates for y_train
    y_dates_test: np.ndarray
        Array of dates for y_test
    test_data: np.ndarray
        Array of prices after the specified end date
    dates_test: np.ndarray
        Array of dates after specified end date
    scaler:
        Fitted PREPROCESS
    """

    scaler = None

    # Pre-process data
    if PREPROCESS == "minmax":
        scaler = MinMaxScaler()

    # Test data is used for forecasting.  Takes the last n_input_days data points.
    # These points are not fed into training

    if s_end_date:
        data = data[data.index <= s_end_date]
        if n_input_days + n_predict_days > data.shape[0]:
            print(
                "Cannot train enough input days to predict with loaded dataframe\n"
            )
            return (
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                True,
            )

    test_data = data.iloc[-n_input_days:]
    train_data = data.iloc[:-n_input_days]

    dates = data.index
    dates_test = test_data.index
    if scaler:
        train_data = scaler.fit_transform(data.values.reshape(-1, 1))
        test_data = scaler.transform(test_data.values.reshape(-1, 1))
    else:
        train_data = data.values.reshape(-1, 1)
        test_data = test_data.values.reshape(-1, 1)

    prices = train_data

    input_dates = []
    input_prices = []
    next_n_day_prices = []
    next_n_day_dates = []

    for idx in range(len(prices) - n_input_days - n_predict_days):
        input_prices.append(prices[idx: idx + n_input_days])  # noqa: E203
        input_dates.append(dates[idx: idx + n_input_days])  # noqa: E203
        next_n_day_prices.append(
            prices[
            idx + n_input_days: idx + n_input_days + n_predict_days  # noqa: E203
            ]
        )
        next_n_day_dates.append(
            dates[
            idx + n_input_days: idx + n_input_days + n_predict_days  # noqa: E203
            ]
        )

    input_dates = np.asarray(input_dates)  # type: ignore
    input_prices = np.array(input_prices)  # type: ignore
    next_n_day_prices = np.array(next_n_day_prices)  # type: ignore
    next_n_day_dates = np.asarray(next_n_day_dates)  # type: ignore

    (
        X_train,
        X_valid,
        y_train,
        y_valid,
        X_dates_train,
        X_dates_valid,
        y_dates_train,
        y_dates_valid,
    ) = train_test_split(
        input_prices,
        next_n_day_prices,
        input_dates,
        next_n_day_dates,
        test_size=test_size,
        shuffle=no_shuffle,
    )
    return (
        X_train,
        X_valid,
        y_train,
        y_valid,
        X_dates_train,
        X_dates_valid,
        y_dates_train,
        y_dates_valid,
        test_data,
        dates_test,
        scaler,
        False,
    )


def forecast(
        input_values: np.ndarray, future_dates: List, model: Sequential, scaler
) -> pd.DataFrame:
    """
    Forecast the stock movement over future days and rescale
    Parameters
    ----------
    input_values: np.ndarray
        Array of values to be fed into the model
    future_dates: List
        List of future dates
    model: Sequential
        Pretrained model
    scaler:
        Fit scaler to be used to 'un-scale' the data

    Returns
    -------
    df_future: pd.DataFrame
        Dataframe of predicted values
    """
    if scaler:
        future_values = scaler.inverse_transform(
            model.predict(input_values.reshape(1, -1, 1)).reshape(-1, 1)
        )
    else:
        future_values = model.predict(input_values.reshape(1, -1, 1)).reshape(-1, 1)

    df_future = pd.DataFrame(
        future_values, index=future_dates, columns=["Predicted Price"]
    )
    return df_future


def get_next_stock_market_days(last_stock_day, n_next_days) -> list:
    """Gets the next stock market day. Checks against weekends and holidays"""
    n_days = 0
    l_pred_days = []
    years: list = []
    holidays: list = []
    while n_days < n_next_days:
        last_stock_day += timedelta(hours=24)
        year = last_stock_day.date().year
        if year not in years:
            years.append(year)
            holidays += us_market_holidays(year)
        # Check if it is a weekend
        if last_stock_day.date().weekday() > 4:
            continue
        # Check if it is a holiday
        if last_stock_day.strftime("%Y-%m-%d") in holidays:
            continue
        # Otherwise stock market is open
        n_days += 1
        l_pred_days.append(last_stock_day)

    return l_pred_days


def us_market_holidays(years) -> list:
    """Get US market holidays"""
    if isinstance(years, int):
        years = [
            years,
        ]
    # https://www.nyse.com/markets/hours-calendars
    market_holidays = [
        "Martin Luther King Jr. Day",
        "Washington's Birthday",
        "Memorial Day",
        "Independence Day",
        "Labor Day",
        "Thanksgiving",
        "Christmas Day",
    ]
    #   http://www.maa.clell.de/StarDate/publ_holidays.html
    good_fridays = {
        2010: "2010-04-02",
        2011: "2011-04-22",
        2012: "2012-04-06",
        2013: "2013-03-29",
        2014: "2014-04-18",
        2015: "2015-04-03",
        2016: "2016-03-25",
        2017: "2017-04-14",
        2018: "2018-03-30",
        2019: "2019-04-19",
        2020: "2020-04-10",
        2021: "2021-04-02",
        2022: "2022-04-15",
        2023: "2023-04-07",
        2024: "2024-03-29",
        2025: "2025-04-18",
        2026: "2026-04-03",
        2027: "2027-03-26",
        2028: "2028-04-14",
        2029: "2029-03-30",
        2030: "2030-04-19",
    }
    market_and_observed_holidays = market_holidays + [
        holiday + " (Observed)" for holiday in market_holidays
    ]
    all_holidays = us_holidays(years=years)
    valid_holidays = []
    for date in list(all_holidays):
        if all_holidays[date] in market_and_observed_holidays:
            valid_holidays.append(date)
    for year in years:
        new_Year = datetime.strptime(f"{year}-01-01", "%Y-%m-%d")
        if new_Year.weekday() != 5:  # ignore saturday
            valid_holidays.append(new_Year.date())
        if new_Year.weekday() == 6:  # add monday for Sunday
            valid_holidays.append(new_Year.date() + timedelta(1))
    for year in years:
        valid_holidays.append(datetime.strptime(good_fridays[year], "%Y-%m-%d").date())
    return valid_holidays
