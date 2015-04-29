from datetime import datetime
import sqlite3 as sqlite
import uuid

from sqlalchemy import event
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

    company_id = Column(Integer, primary_key=True)
    company_name = Column(String(20), nullable=False)

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

    def __init__(self, company_name, symbol, exchange_id=None, headquarter=None, year_founded=None, yahoo_sector_id=None, yahoo_industry_id=None, google_sector_id=None, google_industry_id=None, outstanding=None, current_shares=None, current_price=None, current_volume=None, current_p/e=None):
        pass

    def __repr__(self):
        pass
