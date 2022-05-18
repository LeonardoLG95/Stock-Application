from sqlalchemy import Column, String, CHAR, Float, BigInteger, DateTime, ForeignKey, event, DDL, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def random_id():
    import uuid
    id = uuid.uuid4()
    return id.hex


class Symbol(Base):
    __tablename__ = 'symbol'

    symbol = Column(String, primary_key=True)


class StockInfo(Base):
    __tablename__ = 'stock_info'

    symbol = Column(String, ForeignKey("symbol.symbol"), nullable=False, primary_key=True)
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
    __tablename__ = 'last_candle'

    time = Column(DateTime(timezone=False), nullable=False, primary_key=True)
    symbol = Column(String, ForeignKey("symbol.symbol"), nullable=False, primary_key=True)
    resolution = Column(CHAR, nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    macd = Column(Float, nullable=False)
    macd_hist = Column(Float, nullable=False)
    macd_signal = Column(Float, nullable=False)
    open = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)


class StockPrice(Base):
    __tablename__ = 'stock_price'

    time = Column(DateTime(timezone=False), nullable=False)
    symbol = Column(String, ForeignKey("symbol.symbol"), nullable=False, primary_key=True)
    resolution = Column(CHAR, nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    macd = Column(Float, nullable=False)
    macd_hist = Column(Float, nullable=False)
    macd_signal = Column(Float, nullable=False)
    open = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)


class Buys(Base):
    __tablename__ = 'buys'

    time = Column(DateTime(timezone=False), nullable=False, primary_key=True)
    symbol = Column(String, ForeignKey("symbol.symbol"), nullable=False, primary_key=True)
    eur_price = Column(Float, nullable=False)
    eur_commissions = Column(Float, nullable=False)
    us_price = Column(Float, nullable=False)
    units = Column(Integer, nullable=False, primary_key=True)


class Sells(Base):
    __tablename__ = 'sells'

    time = Column(DateTime(timezone=False), nullable=False, primary_key=True)
    symbol = Column(String, ForeignKey("symbol.symbol"), nullable=False, primary_key=True)
    eur_price = Column(Float, nullable=False)
    eur_commissions = Column(Float, nullable=False)
    us_price = Column(Float, nullable=False)
    units = Column(Integer, nullable=False, primary_key=True)


class Results(Base):
    __tablename__ = 'results'

    id = Column(Integer, default=random_id, primary_key=True)
    symbol = Column(String, ForeignKey("symbol.symbol"), nullable=False)
    eur_result = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)


class BasicFinancials(Base):
    __tablename__ = 'basic_financials'

    period = Column(DateTime(timezone=False), nullable=False, primary_key=True)
    symbol = Column(String, ForeignKey("symbol.symbol"), nullable=False, primary_key=True)
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


class FinancialReport(Base):
    __tablename__ = 'financial_report'

    access_number = Column(String, nullable=False, primary_key=True)
    symbol = Column(String, ForeignKey("symbol.symbol"), nullable=False)
    cik = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    form = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=False), nullable=False)
    end_date = Column(DateTime(timezone=False), nullable=False)
    filed_date = Column(DateTime(timezone=False), nullable=False)
    accepted_date = Column(DateTime(timezone=False), nullable=False)


class ReportConcept(Base):
    __tablename__ = 'report_concept'

    access_number = Column(String, ForeignKey("financial_report.access_number"), nullable=False, primary_key=True)
    label = Column(String, nullable=False)
    concept = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    value = Column(Float, nullable=False)



event.listen(
    StockPrice.__table__,
    'after_create',
    DDL(f"SELECT create_hypertable('{StockPrice.__tablename__}', 'time');"),
)

event.listen(
    BasicFinancials.__table__,
    'after_create',
    DDL(f"SELECT create_hypertable('{BasicFinancials.__tablename__}', 'period');"),
)
