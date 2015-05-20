import os, sys
import logging
from savant.db import session
from savant.db.models import Company, Exchange, Industry, Sector, Underwriter, CompanyUnderwriterAssociation
from savant import scraper
import time

logging.basicConfig()
logging.getLogger("savant").setLevel(logging.DEBUG)

symbols = scraper.get_symbols("NASDAQ")
symbols += scraper.get_symbols("NYSE")

unwr_dict = scraper.get_underwriters()
count = 0
known_exchs = set()
known_industries = set()
known_sectors = set()
known_unwrs = set()

for symbol in symbols:
    count += 1
    if count % 10 == 0:
        print count
    if "-" in symbol:
        continue

    if Company.query.filter_by(symbol=symbol).first():
        continue

    data = scraper.scrape_nasdaq(symbol)
    if not data:
        continue
    elif len(data.keys()) == 1:
        data.update(scraper.scrape_yahoo(symbol, full=True))
    else:
        data.update(scraper.scrape_yahoo(symbol))

    if len(data) == 1:
        continue

    if Company.query.filter_by(name=data["name"]).first():
        continue

    if "exchange" in data:
        if data["exchange"] not in known_exchs:
            print >> sys.stderr, data["exchange"]
            exch = Exchange(name=data["exchange"])
            session.add(exch)
            session.commit()
            known_exchs.add(data["exchange"])
        else:
            exch = Exchange.query.filter_by(name=data["exchange"]).first()
        del data["exchange"]
        data["exchange_id"] = exch.id
 
    if "industry" in data:
        if data["industry"] not in known_industries:
            indus = Industry(name=data["industry"])
            session.add(indus)
            session.commit()
            known_industries.add(data["industry"])
        else:
            indus = Industry.query.filter_by(name=data["industry"]).first()
        del data["industry"]
        data["industry_id"] = indus.id

    if "sector" in data:
        if data["sector"] not in known_sectors:
            sect = Sector(name=data["sector"])
            session.add(sect)
            session.commit()
            known_sectors.add(data["sector"])
        else:
            sect = Sector.query.filter_by(name=data["sector"]).first()
        del data["sector"]
        data["sector_id"] = sect.id

    comp = Company(**data)
    session.add(comp)
    session.commit()

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

session.commit()

session.close()
