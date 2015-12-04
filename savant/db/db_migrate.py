# This tool is for database migration. It is mainly for adding, deleting columes of existing database:
#step 1: Edit new schema
#step 2: Edit migration code, map old columes to new columes
#step 3: Execute the script
#step 4: replace the database with the existing database file
#step 5: replace schema in model.py with the new schema

# to add a new colume, add it in the schema class, dont use nullable=False
# to remove a colume, pop the key from the corresponding dict object



from datetime import date
from random import randint
import sqlite3 as sqlite

from sqlalchemy import create_engine
from sqlalchemy import (Boolean, Column, Date, Enum, ForeignKey, Index,
                        Integer, Float, String, Text, TypeDecorator, event,
                        Sequence, Table, DateTime)
from sqlalchemy.orm import relationship, backref, exc, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import savant.db
import savant.db.models

CBase = declarative_base()


####################Edit here for new schema#######################
class Company(CBase):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    # Company ticker symbol
    symbol = Column(String(10), nullable=False, unique=True)

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
        #params["date_updated"] = date.today()
        self.__dict__.update(params)

    def clone(self, params):
        self.__dict__.update(params)

class Exchange(CBase):
    __tablename__ = "exchange"

    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False, unique=True)

    company = relationship("Company", backref="exchange")

    def __init__(self, name):
        #self.company_id = company_id
        self.name = name

    def clone(self, params):
        self.__dict__.update(params)

    def __repr__(self):
        return "<Exchange(name='%s')>" % (self.name)


class Sector(CBase):
    __tablename__ = "sector"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)

    company = relationship("Company", backref="sector")

    def __init__(self, name):
        self.name = name

    def clone(self, params):
        self.__dict__.update(params)

    def __repr__(self):
        return "<Sector(name='%s')>" % self.name


class Industry(CBase):
    __tablename__ = "industry"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)

    company = relationship("Company", backref="industry")

    def __init__(self, name):
        self.name = name

    def clone(self, params):
        self.__dict__.update(params)

    def __repr__(self):
        return "<Industry(name='%s')>" % self.name


class CompanyUnderwriterAssociation(CBase):
    __tablename__ = "company_underwriter_association"

    company_id = Column(Integer, ForeignKey("company.id"), primary_key=True)
    underwriter_id = Column(Integer, ForeignKey("underwriter.id"), primary_key=True)
    lead = Column(Boolean)
    company = relationship("Underwriter", backref="companies")

    def __init__(self):
        self.company_id = company_id
        self.underwriter_id = underwriter_id
        self.lead = lead

    def clone(self, params):
        self.__dict__.update(params)


class Underwriter(CBase):
    __tablename__ = "underwriter"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    def clone(self, params):
        self.__dict__.update(params)

    def __repr__(self):
        return "<Underwriter(name='%s')>" % self.name


class IPOInfoUrl(CBase):
    __tablename__ = "ipo_url"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    symbol = Column(String(10), nullable=False, unique=True)
    url = Column(String(100), unique=True)

    def __init__(self, name, symbol, url):
        self.name = name
        self.symbol = symbol
        self.url = url

    def clone(self, params):
        self.__dict__.update(params)

    def __repr__(self):
        return "<IPOInfoURL(company_name='%s', symbol='%s', url='%s')>" % (self.name, self.symbol, self.url)


class HistoricalIPO(CBase):
    __tablename__ = "historical_ipo"

    company_id = Column(Integer, ForeignKey("company.id"), primary_key=True)

    ipo_date = Column(Date)
    price = Column(Float)
    shares = Column(Integer)
    outstanding = Column(Integer)
    scoop_rating = Column(Integer)

    # Related to first day trading
    open_vol = Column(Integer)
    first_opening_price = Column(Float)
    first_closing_price = Column(Float)
    first_trade_time = Column(String)
    first_day_high = Column(Float)
    first_day_high_percent_change = Column(Float)
    first_day_low = Column(Float)
    first_day_low_percent_change = Column(Float)
    first_day_volume = Column(Integer)

    # Related to finance
    revenue = Column(Integer)
    net_income = Column(Integer)
    total_assets = Column(Integer)
    total_liability = Column(Integer)
    stakeholder_equity = Column(Integer)
    validity = Column(Integer)



    company = relationship("Company", foreign_keys='HistoricalIPO.company_id')

    def __init__(self, **params):
        self.__dict__.update(params)

    def __repr__(self):
        return "<Historical_IPO(company_id='%s', ipo_date='%s', price='%s', shares='%s', outstanding='%s', scoop_rating='%s')>" % (self.company_id, self.ipo_date, self.price, self.shares, self.outstanding, self.scoop_rating)


class PostIPOPriceAT(CBase):
    __tablename__ = "post_ipo_price_at"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id"), primary_key=False)

    date= Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)

    company = relationship("Company", foreign_keys='PostIPOPriceAT.company_id')
    __table_args__ = (UniqueConstraint('company_id', 'date', name='uix_1'), )


    def __init__(self, **params):
        self.__dict__.update(params)

    def __repr__(self):
        return "<Post_IPO_Price_AT(company_id='%s', datetime='%s', open='%s', high='%s', low='%s', close='%s', volume='%s')>" % (self.company_id, self.datetime, self.open, self.high, self.low, self.close, self.volume)

class PostIPOPriceYahoo(CBase):
    __tablename__ = "post_ipo_price_yh"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id"), primary_key=False)

    date= Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)

    company = relationship("Company", foreign_keys='PostIPOPriceYahoo.company_id')
    __table_args__ = (UniqueConstraint('company_id', 'date', name='uix_1'), )


    def __init__(self, **params):
        self.__dict__.update(params)

    def __repr__(self):
        return "<Post_IPO_Price_Yh(company_id='%s', datetime='%s', open='%s', high='%s', low='%s', close='%s', volume='%s')>" % (self.company_id, self.datetime, self.open, self.high, self.low, self.close, self.volume)

####################End of new schema ######################


#####################Edit following to move the data from old schema to new schema

#create a new database with the above schema
import os
newdbpath= './savant_new.db'
if os.path.exists(newdbpath):
   os.remove(newdbpath)
dest_engine = create_engine('sqlite:///./savant_new.db')
dest_session= sessionmaker(dest_engine)
dest_session.configure(bind=dest_engine)
CBase.metadata.create_all(dest_engine)
s= dest_session()

print "must copy exchange, sector, industry tables first"
exchanges = savant.db.models.Exchange.query.all()
for ex in exchanges:
   nex_dict = ex.__dict__.copy()
   if '_sa_instance_state' in nex_dict.keys():
      nex_dict.pop("_sa_instance_state")
   nex = Exchange("")
   nex.clone(nex_dict)
   s.add(nex)
s.commit()

sectors = savant.db.models.Sector.query.all()
for sec in sectors:
   nsec_dict = sec.__dict__.copy()
   if '_sa_instance_state' in nsec_dict.keys():
      nsec_dict.pop("_sa_instance_state")
   nsec = Sector("")
   nsec.clone(nsec_dict)
   s.add(nsec)
s.commit()

inds = savant.db.models.Industry.query.all()
for ind in inds:
   nind_dict = ind.__dict__.copy()
   if '_sa_instance_state' in nind_dict.keys():
      nind_dict.pop("_sa_instance_state")
   nind = Industry("")
   nind.clone(nind_dict)
   s.add(nind)
s.commit()

print "then copy company table"
cs = savant.db.models.Company.query.all()
for c in cs:
   nc_dict = c.__dict__.copy()
   if '_sa_instance_state' in nc_dict.keys():
      nc_dict.pop("_sa_instance_state")
   nc = Company(**nc_dict)
   s.add(nc)
s.commit()

print "copy ipo_url which is not dependent on any table"
iius = savant.db.models.IPOInfoUrl.query.all()
for iiu in iius:
   niiu_dict = iiu.__dict__.copy()
   if '_sa_instance_state' in niiu_dict.keys():
      niiu_dict.pop("_sa_instance_state")
   niiu = IPOInfoUrl("", "", "")
   niiu.clone(niiu_dict)
   s.add(niiu)
s.commit()

print "copy underwriter before CompanyUnderwriterAssociation" 
us = savant.db.models.Underwriter.query.all()
for u in us:
   nu_dict = u.__dict__.copy()
   if '_sa_instance_state' in nu_dict.keys():
      nu_dict.pop("_sa_instance_state")
   nu = Underwriter("")
   nu.clone(nu_dict)
   s.add(nu)
s.commit()

cuas = savant.db.models.CompanyUnderwriterAssociation.query.all()
for cua in cuas:
   ncua_dict = cua.__dict__.copy()
   if '_sa_instance_state' in ncua_dict.keys():
      ncua_dict.pop("_sa_instance_state")
   ncua = CompanyUnderwriterAssociation()
   ncua.clone(ncua_dict)
   s.add(ncua)
s.commit()

print "now copy HistoricalIPO and PostIPOPrice table"
his = savant.db.models.HistoricalIPO.query.all()
for hi in his:
   hi_dict = hi.__dict__
   if '_sa_instance_state' in hi_dict.keys():
      hi_dict.pop("_sa_instance_state")
   nhi = HistoricalIPO(**hi_dict)
   s.add(nhi)
s.commit()

#change datetime to date
pips = savant.db.models.PostIPOPrice.query.all()
for pip in pips:
   pip_dict = pip.__dict__
   #pip_dict["date"]=pip_dict["datetime"].date()
   #pip_dict.pop("datetime")
   if '_sa_instance_state' in pip_dict.keys():
      pip_dict.pop("_sa_instance_state")
   new_pip = PostIPOPrice(**pip_dict)
   s.add(new_pip)
s.commit()
