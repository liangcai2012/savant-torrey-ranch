import os, sys
import logging
from savant.db import session
from savant.db.models import Company, Exchange, Industry, Sector
from savant import scraper
import time

logging.basicConfig()
logging.getLogger("savant").setLevel(logging.DEBUG)

symbols = scraper.get_symbols("NASDAQ")
symbols += scraper.get_symbols("NYSE")

#unwr_dict = scraper.get_underwriters()
count = 0

for symbol in symbols:
    count += 1
    if count % 10 == 0:
        print count
    if "-" in symbol:
        continue

    comp = scraper.get_company_overview(symbol)
#    if comp and not Company.query.filter_by(symbol=comp.symbol).first() and not Company.query.filter_by(name=comp.name).first():
    if comp:
        if not Company.query.filter_by(symbol=comp.symbol).first():
            session.add(comp)
            session.commit()
        else:
            print "Company exists in db"


    """
    if symbol in unwr_dict:
        underwriters = [u.strip() for u in unwr_dict[symbol].split("/")]
        for u in underwriters:
            if u in known_unwrs:
                unwr = Underwriter.query.filter_by(name=u).first()
            else:
                unwr = Underwriter(u)
                known_unwrs.add(u)
            session.add(unwr)
            session.commit()
            a = CompanyUnderwriterAssociation(company_id=comp.id, underwriter_id=unwr.id, lead=True)
            comp.underwriters.append(a)
            session.commit()
    """

session.close()
