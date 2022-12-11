from sqlalchemy import (
    Column,
    String,
    CHAR,
    Float,
    BigInteger,
    DateTime,
    ForeignKey,
    event,
    DDL,
    Integer,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Symbol(Base):
    __tablename__ = "symbol"

    symbol = Column(String, primary_key=True)


class StockInfo(Base):
    __tablename__ = "stock_info"

    id = Column(BigInteger, nullable=False, autoincrement=True, primary_key=True)
    symbol = Column(String, ForeignKey("symbol.symbol"), nullable=False)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    ipo = Column(DateTime(timezone=False), nullable=False)
    market_capitalization = Column(BigInteger, nullable=False)
    share_outstanding = Column(Float, nullable=False)
    website = Column(String, nullable=False)
    industry = Column(String, nullable=False)


class LastCandle(Base):
    __tablename__ = "last_candle"

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


class MonthlyStockPrice(Base):
    __tablename__ = "monthly_stock_price"

    id = Column(BigInteger, nullable=False, autoincrement=True, primary_key=True)
    time = Column(DateTime(timezone=False), nullable=False)
    symbol = Column(String, ForeignKey("symbol.symbol"), nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    macd = Column(Float, nullable=False)
    macd_hist = Column(Float, nullable=False)
    macd_signal = Column(Float, nullable=False)
    open = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)


class WeeklyStockPrice(Base):
    __tablename__ = "weekly_stock_price"

    id = Column(BigInteger, nullable=False, autoincrement=True, primary_key=True)
    time = Column(DateTime(timezone=False), nullable=False)
    symbol = Column(String, ForeignKey("symbol.symbol"), nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    macd = Column(Float, nullable=False)
    macd_hist = Column(Float, nullable=False)
    macd_signal = Column(Float, nullable=False)
    open = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)


class DailyStockPrice(Base):
    __tablename__ = "daily_stock_price"

    id = Column(BigInteger, nullable=False, autoincrement=True, primary_key=True)
    time = Column(DateTime(timezone=False), nullable=False)
    symbol = Column(String, ForeignKey("symbol.symbol"), nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    macd = Column(Float, nullable=False)
    macd_hist = Column(Float, nullable=False)
    macd_signal = Column(Float, nullable=False)
    open = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)


class BasicFinancials(Base):
    __tablename__ = "basic_financials"

    period = Column(DateTime(timezone=False), nullable=False, primary_key=True)
    symbol = Column(
        String, ForeignKey("symbol.symbol"), nullable=False, primary_key=True
    )
    time_window = Column(String, nullable=False, primary_key=True)
    cash_ratio = Column(Float)
    current_ratio = Column(Float)
    ebit_per_share = Column(Float)
    eps = Column(Float)
    gross_margin = Column(Float)
    longterm_debt_total_asset = Column(Float)
    longterm_debt_total_capital = Column(Float)
    longterm_debt_total_equity = Column(Float)
    net_debt_to_total_capital = Column(Float)
    net_debt_to_total_equity = Column(Float)
    net_margin = Column(Float)
    operating_margin = Column(Float)
    pretax_margin = Column(Float)
    sales_per_share = Column(Float)
    sga_to_sale = Column(Float)
    total_debt_to_equity = Column(Float)
    total_debt_to_total_asset = Column(Float)
    total_debt_to_total_capital = Column(Float)
    total_ratio = Column(Float)
    book_value = Column(Float)
    ev = Column(Float)
    quick_ratio = Column(Float)
    fcf_margin = Column(Float)
    roa = Column(Float)
    roe = Column(Float)
    pb = Column(Float)
    pe = Column(Float)


class FinancialReport(Base):
    __tablename__ = "financial_report"

    id = Column(String, nullable=False, primary_key=True)
    access_number = Column(String, nullable=False)
    symbol = Column(String, ForeignKey("symbol.symbol"), nullable=False)
    frequency = Column(String, nullable=False)
    cik = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    form = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=False), nullable=False)
    end_date = Column(DateTime(timezone=False), nullable=False)
    filed_date = Column(DateTime(timezone=False), nullable=False)
    accepted_date = Column(DateTime(timezone=False), nullable=False)


class ReportConcept(Base):
    __tablename__ = "report_concept"

    id = Column(BigInteger, nullable=False, autoincrement=True, primary_key=True)
    financial_report = Column(String, ForeignKey("financial_report.id"), nullable=False)
    label = Column(String, nullable=False)
    concept = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    value = Column(Float, nullable=False)


event.listen(
    MonthlyStockPrice.__table__,
    "after_create",
    DDL(f"SELECT create_hypertable('{MonthlyStockPrice.__tablename__}', 'time');"),
)

event.listen(
    WeeklyStockPrice.__table__,
    "after_create",
    DDL(f"SELECT create_hypertable('{WeeklyStockPrice.__tablename__}', 'time');"),
)

event.listen(
    DailyStockPrice.__table__,
    "after_create",
    DDL(f"SELECT create_hypertable('{DailyStockPrice.__tablename__}', 'time');"),
)

event.listen(
    BasicFinancials.__table__,
    "after_create",
    DDL(f"SELECT create_hypertable('{BasicFinancials.__tablename__}', 'period');"),
)
