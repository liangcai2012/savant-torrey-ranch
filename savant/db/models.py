from datetime import date
from random import randint
import sqlite3 as sqlite

from sqlalchemy import (Boolean, Column, Date, Enum, ForeignKey, Index,
                        Integer, Float, String, Text, TypeDecorator, event,
                        Sequence, Table)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import relationship, backref

from savant import db


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    See http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#foreign-key-support
    """
    if isinstance(dbapi_connection, sqlite.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()


class Company(db.Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    # Company ticker symbol
    symbol = Column(String(10), nullable=False)

    # Exchange
    exchange_id = Column(Integer, ForeignKey("exchange.id"))
    
    # Sector
    sector_id = Column(Integer, ForeignKey("sector.id"))

    # Industry
    industry_id = Column(Integer, ForeignKey("industry.id"))

    # Company primary location
    #headquarter = Column(String(100))
    
    # Market cap
    market_cap = Column(Integer)
    
    # Public shares as of the date this table is updated
    float_shares = Column(Integer)

    # Closing price as of the date this table is updated
    prev_close = Column(Float)

    # Volume as of the date this table is updated
    prev_volume = Column(Integer)

    # P/E ratio as of the date this table is updated
    trailing_pe = Column(Float)

    # Beta rating for NASDAQ tickers
    nasdaq_beta = Column(Float)

    # Date of the last update
    date_updated = Column(Date)

    # Relationship
    underwriters = relationship("CompanyUnderwriterAssociation")

    def __init__(self, **params):
        params["date_updated"] = date.today()
        self.__dict__.update(params)

    def __repr__(self):
        return "<Company(name='%s', symbol='%s', exchange_id='%s', market_cap='%s', float_shares='%s', previous_close='%s', previous_volume='%s', trailing_p/e='%s', beta='%s', date_updated='%s')>" % (self.name, self.symbol, self.exchange_id, self.market_cap, self.float_shares, self.prev_close, self.prev_volume, self.trailing_pe, self.nasdaq_beta, self.date_updated)


class Exchange(db.Base):
    __tablename__ = "exchange"

    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False, unique=True)

    company = relationship("Company", backref="exchange")

    def __init__(self, name):
        #self.company_id = company_id
        self.name = name

    def __repr__(self):
        return "<Exchange(name='%s')>" % (self.name)


class Sector(db.Base):
    __tablename__ = "sector"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)

    company = relationship("Company", backref="sector")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Sector(name='%s')>" % self.name


class Industry(db.Base):
    __tablename__ = "industry"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)

    company = relationship("Company", backref="industry")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Industry(name='%s')>" % self.name


class CompanyUnderwriterAssociation(db.Base):
    __tablename__ = "company_underwriter_association"

    company_id = Column(Integer, ForeignKey("company.id"), primary_key=True)
    underwriter_id = Column(Integer, ForeignKey("underwriter.id"), primary_key=True)
    lead = Column(Boolean)
    company = relationship("Underwriter", backref="companies")


class Underwriter(db.Base):
    __tablename__ = "underwriter"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Underwriter(name='%s')>" % self.name


class IPOInfoUrl(db.Base):
    __tablename__ = "ipo_url"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    symbol = Column(String(10), nullable=False, unique=True)
    url = Column(String(100), unique=True)

    def __init__(self, name, symbol, url):
        self.name = name
        self.symbol = symbol
        self.url = url

    def __repr__(self):
        return "<IPOInfoURL(company_name='%s', symbol='%s', url='%s')>" % (self.name, self.symbol, self.url)


class HistoricalIPO(db.Base):
    __tablename__ = "historical_ipo"
    
    company_id = Column(Integer, ForeignKey("company.id"), primary_key=True)

    ipo_date = Column(Date)
    price = Column(Float)
    shares = Column(Integer)
    outstanding = Column(Integer)
    scoop_rating = Column(Integer)

    # Related to first day trading
    first_opening_price = Column(Float)
    first_closing_price = Column(Float)
    first_trade_time = Column(String)
    first_day_high = Column(Float)
    first_day_high_percent_change = Column(Float)
    first_day_low = Column(Float)
    first_day_low_percent_change = Column(Float)
    first_day_volume = Column(Integer)
    
    def __init__(self, **params):
        self.__dict__.update(params)

    def __repr__(self):
        return "<Historical_IPO(company_id='%s', ipo_date='%s', price='%s', shares='%s', outstanding='%s', scoop_rating='%s')>" % (self.company_id, self.ipo_date, self.price, self.shares, self.outstanding, self.scoop_rating)
