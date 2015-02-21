from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship, backref, exc, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

db_dir = "../../../../savant/data/" 
Base = declarative_base()

class Exch(Base):
	__tablename__="exch"
	id = Column(Integer, primary_key=True)
	name = Column(String)

class GSector(Base):
	__tablename__="gsector"
	id = Column(Integer, primary_key=True)
	name = Column(String)

class GIndustry(Base):
	__tablename__="gindustry"
	id = Column(Integer, primary_key=True)
	name = Column(String)

class YSector(Base):
	__tablename__="ysector"
	id = Column(Integer, primary_key=True)
	name = Column(String)

class YIndustry(Base):
	__tablename__="yindustry"
	id = Column(Integer, primary_key=True)
	name = Column(String)

class SymStatic(Base):
	__tablename__="symbalstatic"
	symbol = Column(String, primary_key=True)
	share_num = Column(Integer)
	company_name = Column(String, nullable=False)
	exch_id = Column(Integer, ForeignKey('exch.id'), nullable=False)
	exchange = relationship(Exch, backref=backref('stocks', uselist=True))
	gsector_id = Column(Integer, ForeignKey('gsector.id'))
	gsector = relationship(GSector, backref=backref('stocks', uselist=True))
	gindustry_id= Column(Integer, ForeignKey('gindustry.id'))
	gindustry= relationship(GIndustry, backref=backref('stocks', uselist=True))
	ysector_id = Column(Integer, ForeignKey('ysector.id'))
	ysector = relationship(YSector, backref=backref('stocks', uselist=True))
	yindustry_id= Column(Integer, ForeignKey('yindustry.id'))
	yindustry= relationship(YIndustry, backref=backref('stocks', uselist=True))

class StaticInfo:
	def __init__(self):
		pass

	def createDB(self):
		pass

	def open(self):
		engine = create_engine('sqlite:///'+db_dir+'staticinfo.sqlite')
		session = sessionmaker()
		session.configure(bind=engine)
		Base.metadata.create_all(engine)
		self.s = session()
		self.exchangelist = self.s.query(Exch).all()
		self.gsectlist = self.s.query(GSector).all()
		self.gindlist = self.s.query(GIndustry).all()
		self.ysectlist = self.s.query(YSector).all()
		self.yindlist = self.s.query(YIndustry).all()


	def close(self):
		self.s.close()
		

	def update(self, sym, exch, shares, cname, gsect, gind, ysect, yind):
		if sym is "" or sym is None:
			print "fail to add record: sym cannot be empty"
			return
		try:
			stock = self.s.query(SymStatic).filter(SymStatic.symbol==sym).one()

		except exc.NoResultFound:
			if exch == None or exch == "":
				print "fail to add record: exchange cannot be empty"
				return
			if cname == None or exch == "":
				print "fail to add record: company name cannot be empty"
				return
			if shares == None or shares <= 0:
				print "fail to add record: invalid share number"
				return
			stock = SymStatic(symbol = sym)

		except exc.MultipleResultsFound:
			print "database error, multiple records exist for symbol = ", sym 
			return

		if shares != None and shares > 0: 
			if shares != stock.share_num:
				print 'set share nem'
				stock.share_num = shares 
		if cname != None and cname != "":
			if	cname != stock.company_name:
				stock.company_name = cname
		if exch != None and exch != "":
			if stock.exchange==None or exch != stock.exchange.name:
				try:
					this_exch = self.s.query(Exch).filter(Exch.name == exch).one()
					stock.exchange = this_exch
				except exc.NoResultFound:
					stock.exchange = Exch(name=exch)
				except exc.MultipleResultsFound:
					print "database error, multiple records exist for exchange = ", exch
					return
		if stock.gsector == None or gsect != stock.gsector.name:
			stock.gsector = GSector(name = gsect)  
		if stock.gindustry == None or gind != stock.gindustry.name:
			stock.gindustry= GIndustry(name = gind)  
		if stock.ysector == None or ysect != stock.ysector.name:
			stock.ysector = YSector(name = ysect)  
		if stock.yindustry == None or yind != stock.yindustry.name:
			stock.yindustry= YIndustry(name = yind)  

		print stock.exchange.id, stock.exchange.name

		self.s.add(stock)
		self.s.commit()

	
	def getstocklist(self, exch):
		pass
	
	def getstockbygsect(self, gsect):
		pass

	def getstockbyysect(self, ysect):
		pass

	def getstockbygind(self, gind):
		pass

	def getstockbyyind(self, yind):
		pass


si = StaticInfo()
si.open()
si.update("QQQ", "NYSE", 12000, "QQQ ETF", "", "", "", None)
si.update("QQQ", "NASDAQ", 1000, "QQQ ETF", "", "", "", None)
si.update("ABC", "NASDAQ", "200", "QQQ ETF", "ENERGY", "OIL", "", None)
si.update("ABC", "NYSE", "200", "QQQ ETF", "ENERGY", "OIL", "", None)
si.close()


