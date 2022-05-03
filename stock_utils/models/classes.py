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

    symbol = Column(String, ForeignKey("symbol.symbol"), primary_key=True)
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

    time = Column(DateTime(timezone=False), primary_key=True)
    symbol = Column(String, ForeignKey("symbol.symbol"), primary_key=True)
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
    symbol = Column(String, ForeignKey("symbol.symbol"), primary_key=True)
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
    symbol = Column(String, ForeignKey("symbol.symbol"), primary_key=True)
    eur_price = Column(Float, nullable=False)
    eur_commissions = Column(Float, nullable=False)
    us_price = Column(Float, nullable=False)
    units = Column(Integer, nullable=False, primary_key=True)


class Sells(Base):
    __tablename__ = 'sells'

    time = Column(DateTime(timezone=False), nullable=False, primary_key=True)
    symbol = Column(String, ForeignKey("symbol.symbol"), primary_key=True)
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


event.listen(
    StockPrice.__table__,
    'after_create',
    DDL(f"SELECT create_hypertable('{StockPrice.__tablename__}', 'time');"),
)
