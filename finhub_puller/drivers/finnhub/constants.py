from env import FINHUB_TOKEN

END_POINTS = {
    "base_url": "https://finnhub.io/api/v1/",
    "indices": {
        "^NDX",
        "^DJI",
        "^SP500-50",
        "^SP500-25",
        "^SP500-30",
        "^GSPE",
        "^SP500-40",
        "^SP500-35",
        "^SP500-20",
        "^SP500-15",
        "^SP500-60",
        "^SP500-45",
    },
    "index_endpoint": lambda index: f"index/constituents?symbol={index}",
    "stock_price_endpoint": lambda symbol, resolution, to_: f"indicator?symbol={symbol}&resolution={resolution}&from=0&to={to_}&indicator=macd",
    "stock_info_endpoint": lambda symbol: f"stock/profile2?symbol={symbol}",
    "stock_basic_financials": lambda symbol: f"stock/metric?symbol={symbol}&metric=all",
    "stock_financial_reports": lambda symbol, frequency: f"stock/financials-reported?symbol={symbol}&freq={frequency}",
    "resolutions": ["D", "W", "M"],
    "crypto": {"COINBASE:ETH-EUR", "COINBASE:BTC-EUR"},
    "crypto_exchange": "COINBASE",
    "crypto_endpoint": lambda symbol, resolution, to_: f"indicator?symbol={symbol}&resolution={resolution}&from=0&to={to_}&indicator=macd",
}

EXPECTED_RESPONSE_KEYS = {
    "candle_keys": ("t", "c", "h", "l", "macd", "macdHist", "macdSignal", "o", "v"),
    "info_keys": (
        "name",
        "country",
        "currency",
        "exchange",
        "ipo",
        "marketCapitalization",
        "shareOutstanding",
        "weburl",
        "finnhubIndustry",
    ),
    "report_keys": (
        "accessNumber",
        "symbol",
        "cik",
        "year",
        "quarter",
        "form",
        "startDate",
        "endDate",
        "filedDate",
        "acceptedDate",
        "report",
    ),
}

API_TOKEN = f"&token={FINHUB_TOKEN}"

"""
^SP500-50	S&P Communication Services Select Sector
^SP500-25	S&P Consumer Discretionary Select Sector
^SP500-30	S&P Consumer Staples Select Sector
^GSPE	S&P Energy Select Sector
^SP500-40	S&P Financial Select Sector
^SP500-35	S&P Health Care Select Sector
^SP500-20	S&P Industrial Select Sector
^SP500-15	S&P Materials Select Sector
^SP500-60	S&P Real Estate Select Sector
^SP500-45	S&P Technology Select Sector

from has to be 0 if not, the MACD is calculated based on the days you pull
"""
