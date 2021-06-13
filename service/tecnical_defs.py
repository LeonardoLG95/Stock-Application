import random
import numpy


def rsi(prices: numpy):
    prices = prices[-14:]
    i = 1
    avg_up = 0
    avg_down = 0

    while i < 14:
        difference = percent(prices[i], prices[i-1])
        if 0 < difference:
            avg_up += difference
        else:
            avg_down += -difference
        i += 1

    avg_up = division(avg_up, 14)
    avg_down = division(avg_down, 14)

    rs = division(avg_up, avg_down)
    result = 100 - division(100, (1+rs))

    return result


def macd(prices):
    ema1 = ema(prices, 12)
    ema2 = ema(prices, 26)

    i = 0
    result = []
    while i < len(ema2):
        result.append(ema1[i+14]-ema2[i])
        i += 1

    return result


def average_macd_values(macd_value: list, start_points: list, end_points: list, is_up: bool):
    result = 0
    i = 0
    while i < len(start_points):
        section = macd_value[start_points[i]:end_points[i]]
        if section:
            if is_up:
                result += max(section)
            else:
                result += min(section)

        i += 1

    return division(result, i)


def max_macd(macd_result, signal):
    # difference between macd and signal
    signal_i = len(macd_result)-len(signal)

    start_up_points_list = []
    end_up_points_list = []
    start_point_up = None
    end_point_up = None
    first_up = True

    start_down_points_list = []
    end_down_points_list = []
    start_point_down = None
    end_point_down = None
    first_down = True

    i = 0
    while i < len(macd_result)-signal_i:
        macd_point = macd_result[i + signal_i]
        signal_point = signal[i]

        # positive interval of the macd
        if macd_point > signal_point:
            if first_up:
                start_point_up = i + signal_i
                first_up = False
            end_point_up = i + signal_i

            # save points from start and end of negative interval
            if start_point_down is not None and end_point_down is not None:
                start_down_points_list.append(start_point_down)
                end_down_points_list.append(end_point_down)
                start_point_down = None
                end_point_down = None
                first_down = True

        # negative interval of the macd
        elif macd_point < signal_point:
            if first_down:
                start_point_down = i + signal_i
                first_down = False
            end_point_down = i + signal_i

            # save positive interval of the macd
            if start_point_up is not None and end_point_up is not None:
                start_up_points_list.append(start_point_up)
                end_up_points_list.append(end_point_up)
                start_point_up = None
                end_point_up = None
                first_up = True

        i += 1

    macd_down_avg = average_macd_values(macd_result, start_down_points_list, end_down_points_list, is_up=False)
    values = [macd_down_avg]

    macd_up_avg = average_macd_values(macd_result, start_up_points_list, end_up_points_list, is_up=True)
    values.append(macd_up_avg)
    pass
    return values


def sma(prices, period=0):
    i = 0
    result = 0
    if period != 0:
        prices = prices[-period:]

        while i < period-1:
            result += prices[i]
            i += 1

        result = division(result, period)
    else:
        while i < len(prices):
            result += prices[i]
            i += 1
        result = sma(result, len(prices))

    return result


def ema(prices, period):
    multiplier = division(2, (period + 1))

    i = period-1
    x = 0
    result = []
    while i < len(prices):
        if i == period - 1:
            sma_value = sma(prices, period)
            result.append((prices[i] - sma_value) * multiplier + sma_value)
            x = 0
        else:
            result.append((prices[i] - result[x]) * multiplier + result[x])
            x += 1
        i += 1

    return result


def get_stop(prices, period):
    prices = prices[-period:]
    stop = min(prices) - 1 - random.random()

    return stop


def get_high(prices, period):
    prices = prices[-period:]
    result = max(prices)

    return result


def percent(new, old):
    result = (division((new - old), old)) * 100

    return result


def division(dividend, divisor):
    if dividend != 0 and divisor != 0:
        result = dividend / divisor
    else:
        result = 0

    return result
