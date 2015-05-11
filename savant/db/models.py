from datetime import datetime
from random import randint
import sqlite3 as sqlite

from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Index,
                        Integer, Float, String, Text, TypeDecorator, event,
                        Sequence)
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

    id = Column(Integer, Sequence('company_id_seq'), primary_key=True)
    name = Column(String(20), nullable=False, unique=True)

    # Company ticker symbol
    symbol = Column(String(10), nullable=False)
    
    # ID of the exchange on which the company is listed
    exchange_id = Column(Integer, ForeignKey('exchanges.id'))
    exchange = relationship("Exchange", backref="company")
    
    # Company primary location
    headquarter = Column(String(100))
    
    # Yead of foundation
    year_founded = Column(Integer)
    
    # Sector and industry provided by Yahoo
    yahoo_sector_id = Column(Integer, ForeignKey('sectors.id'))
    yahoo_sector = relationship("Sector", backref="company")
    yahoo_industry_id = Column(Integer, ForeignKey('industries.id'))
    yahoo_industry = relationship("Industry", backref="company")

    # Sector and industry provided by Google
    google_sector_id = Column(Integer, ForeignKey('sectors.id'))
    google_sector = relationship("Sector", backref="company")
    google_industry_id = Column(Integer, ForeignKey('industries.id'))
    google_industry = relationship("Industry", backref="company")

    # Outstanding shares
    outstanding_shares = Column(Float)
    
    # Public shares as of the date this table is updated
    float_shares = Column(Float)

    # Closing price as of the date this table is updated
    previous_close = Column(Float)

    # Volume as of the date this table is updated
    previous_volume = Column(Integer)

    # P/E ratio as of the date this table is updated
    trailing_pe = Column(Float)

    # Date of the last update
    date_updated = Column(DateTime)

    """
    def __init__(self, name, symbol, exchange=None, headquarter=None, year_founded=None, yahoo_sector=None, yahoo_industry=None, google_sector=None, google_industry=None, outstanding=None, current_shares=None, current_price=None, current_volume=None, current_pe=None):
        self.name = name
        self.symbol = symbol
        self.exchange = exchange
        self.headquarter = headquarter
        self.year_founded = year_founded
        self.yahoo_sector_id = yahoo_sector_id
        self.yahoo_industry_id = yahoo_industry_id
        self.google_sector_id = google_sector_id
        self.google_industry_id = google_industry_id
        self.outstanding = outstanding
        self.current_shares = current_shares
        self.current_price = current_price
        self.current_volume = current_volume
        self.current_pe = current_pe
        self.date_updated = str(datetime.now()).split()[0]
    """
    def __init__(self, **params):
        self.__dict__.update(params)


    def __repr__(self):
        return "<Company(name='%s', symbol='%s', current_shares='%s', current_price='%s', current_volume='%s', current_p/e='%s', date_updated='%s')>" % (self.name, self.symbol, self.current_shares, self.current_price, self.current_volume, self.current_p/e, self.date_updated)


class Exchange(db.Base):
    __tablename__ = "exchange"

    id = Column(Integer, Sequence("exchange_id_seq"), primary_key=True)
    name = Column(String(10), nullable=False, unique=True)

    # Country in which the exchange originates
    origin = Column(String(10))

    def __init__(self, name, origin=None):
        self.name = name
        self.origin = origin

    def __repr__(self):
        return "<Exchange(name='%s', origin='%s')>" % (self.name, self.origin)


class Sector(db.Base):
    __tablename__ = "sector"

    id = Column(Integer, Sequence("sector_id_seq"), primary_key=True)
    name = Column(String(20), nullable=False)

    # Provider of the info
    provider = Column(String(10), nullable=False)

    def __init__(self, name, provider):
        self.name = name
        self.provider = provider

    def __repr__(self):
        return "<Sector(name='%s', provider='%s')>" % (self.name, self.provider)


class Industry(db.Base):
    __tablename__ = "industry"

    id = Column(Integer, Sequence("industry_id_seq"), primary_key=True)
    name = Column(String(20), nullable=False)

    # Provider of the info
    provider = Column(String(10), nullable=False)

    def __init__(self, name, provider):
        self.name = name
        self.provider = provider

    def __repr__(self):
        return "<Industry(name='%s', provider='%s')>" % (self.name, self.provider)


class Underwriter(db.Base):
    __tablename__ = "underwriter"

    id = Column(Integer, Sequence("underwriter_id_seq"), primary_key=True)
    name = Column(String(100), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Underwriter(name='%s')>" % self.name


if __name__ == "__main__":
    comp = Company(**{"name": "Apple"})
