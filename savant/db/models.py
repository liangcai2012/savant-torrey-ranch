from datetime import datetime
from random import randint
import sqlite3 as sqlite

from sqlalchemy import event, Sequence
from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Index,
                        Integer, Float, String, Text, TypeDecorator)
from sqlalchemy.engine import Engine

from savant.chihuahua import db


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    See http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#foreign-key-support
    """
    if isinstance(dbapi_connection, sqlite.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()


class Companies(db.Base):
    __tablename__ = "companies"

    id = Column(Integer, Sequence('company_id_seq'), primary_key=True)
    name = Column(String(20), nullable=False, unique=True)

    # Company ticker symbol
    symbol = Column(String(10), nullable=False)
    
    # ID of the exchange on which the company is listed
    exchange_id = Column(Integer, ForeignKey('exchanges.id'))
    
    # Company primary location
    headquarter = Column(String(100))
    
    # Yead of foundation
    year_founded = Column(Integer)
    
    # Sector and industry provided by Yahoo
    yahoo_sector_id = Column(Integer, ForeignKey('sectors.id'))
    yahoo_industry_id = Column(Integer, ForeignKey('industries.id'))

    # Sector and industry provided by Google
    google_sector_id = Column(Integer, ForeignKey('sectors.id'))
    google_industry_id = Column(Integer, ForeignKey('industries.id'))

    # Outstanding shares
    outstanding = Column(Float)
    
    # Public shares as of the date this table is updated
    current_shares = Column(Float)

    # Closing price as of the date this table is updated
    current_price = Column(Float)

    # Volume as of the date this table is updated
    current_volume = Column(Integer)

    # P/E ratio as of the date this table is updated
    current_p/e = Column(Float)

    # Date of the last update
    date_updated = Column(String)


    def __init__(self, name, symbol, exchange_id=None, headquarter=None, year_founded=None, yahoo_sector_id=None, yahoo_industry_id=None, google_sector_id=None, google_industry_id=None, outstanding=None, current_shares=None, current_price=None, current_volume=None, current_p/e=None):
        self.name = name
        self.symbol = symbol
        self.exchange_id = exchange_id
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
        self.current_p/e = current_p/e
        self.date_updated = str(datetime.now()).split()[0]

    def __repr__(self):
        return "<Company(name='%s', symbol='%s', current_shares='%s', current_price='%s', current_volume='%s', current_p/e='%s', date_updated='%s')>" % (self.name, self.symbol, self.current_shares, self.current_price, self.current_volume, self.current_p/e, self.date_updated)
