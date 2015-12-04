#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from bs4 import BeautifulSoup
from savant.db import session, Base
from savant.db.models import Company, IPOInfoUrl, HistoricalIPO, CompanyUnderwriterAssociation, Underwriter 
from savant.scraper import get_soup


def scrape_ipo_underwriter(exp_url):
    uw_data = [] 
    lead_uw_data = [] 
    
    try:
        soup = get_soup(exp_url)
    except:
        print "Unable to reach or parse url:", exp_url
        return None 
    try:
       table = soup.find("div", {"id": "tabpane3"}).div.table
       rows = table.find_all("tr")
       for row in rows:
           key = row.td.text.strip()
           if key == "Lead Underwriter":
               value = normalize_uw_name(row.find_all("td")[1].text.strip(' ').encode('utf-8').lower())
               value = value.decode('utf-8')
               lead_uw_data.append(value)
           if key == "Underwriter":
               value = normalize_uw_name(row.find_all("td")[1].text.strip(' ').encode('utf-8').lower())
               value = value.decode('utf-8')
               uw_data.append(value)
    except IOError:
       print "Unable to parse the page: ", exp_url
       return None 
    return [lead_uw_data, uw_data]

def populate_ipo_underwriter():
    ipo_urls = IPOInfoUrl.query.all()
    for url in ipo_urls:
        comp = Company.query.filter_by(symbol=url.symbol).first()
        if not comp: 
            continue
        hi = HistoricalIPO.query.filter_by(company_id=comp.id).first()
        if not hi:
            continue
        assoc= CompanyUnderwriterAssociation.query.filter_by(company_id=comp.id).first()
        if assoc:
            print "underwriter for", url.symbol, "already in database"
            continue

        exp_url = url.url + '?tab=experts'
        uw_data = scrape_ipo_underwriter(exp_url)
        if uw_data == None:
            continue
        print url.symbol, uw_data
        for i in [0,1]:
            for uw_item in uw_data[i]:
                if not uw_item:
                    continue
                uw = Underwriter.query.filter_by(name = uw_item).first()
                if not uw:
                    uw = Underwriter(name=uw_item)
                    session.add(uw)
                    session.commit()
                
                assoc= CompanyUnderwriterAssociation.query.filter_by(company_id=comp.id).filter_by(underwriter_id = uw.id).first()
                if assoc:
                    continue

                if i == 0:
                    lead = True
                else:
                    lead = False
                assoc = CompanyUnderwriterAssociation(comp.id, uw.id, lead)
                session.add(assoc)
                session.commit()

def reduce_list():
    from sets import Set
    name_set = Set()
    with open('../utils/uw_list', 'r') as f:
        for line in f:
            #if not line.startswith('297'):
            #    continue
            name_set.add(normalize_uw_name(line.strip().split('|')[1].lower()))
    name_list = list(name_set)
    name_list.sort()
    for name in name_list:
        print '|',name,'|'
    
def normalize_uw_name(name):
    postfix_list = ['capital markets', 'capital group', 'capital partners', 'capital', 'captial', 'financial group', ' group', 'global markets', 'global trading', 'securities', 'investment banking', 'investment bank', 'capital advisors', 'research associates', 'research and trading', 'research partners', 'investment research', 'research', 'trading', 'investment', 'financial markets', 'financial services', 'financial', 'markets', 
    'usa', 'americas', '(usa)', '(uk)', '(publ)', 
    'and company', 'and co', 'and comany', 'and co international', 'incorporated', 'limited', 'corp', 'and partners', 'corporation', 'incorporate', 'and associates',  'ltd', 'companies', 'company', 'international plc', 'partners', 
    'nv/sa', ' llc', ' inc', ' lllp', ' lp', ' asa', ' sa', ' nv', ' plc', ' as', ' llp' ]
    
    alias_list = {"oppenhemier": "oppenheimer", 'wr hambrecht': 'wr', 'wedbush morgan': 'wedbush', "tod's":"tods", 'sander':'sandler', 'leerink swann': 'leerink', "lazard fr\xc3\xa8res":"lazard", 'kotak mahindra': "kotak", "credit suisse first boston": "credit suisse", "dnb nor": "dnb", "fearnley fonds": "fearnley", "brean murray carret": "brean", "blaylock robert van": "blaylock beal van", "bbva banco continental": "bbva", "bmo nesbitt burns": "bmo", "coöperatieve":"coperatieve", "natixis bleichroeder": "natixis", "keffe":"keefe", "itau bba":"itau", "abn amro bank":"abn amro", "canaccord adams": "canaccord genuity"}
    #if it contains ;, only use the string before it
    if ' a ' in name:  #something a division of ...
        name = name[:name.index(' a ')]
    
    # to reduce the postfix numbers
    name = name.replace('&', 'and')

    #remove all comma and dots
    name = name.replace(',', '')
    name = name.replace(';', '')
    name = name.replace('.', '')
    name = name.replace('\xc2\xa0', ' ')
    name = name.replace('\xe2\x80\x99', "'")
    name = name.replace('\xc2\xba', "u")
    name = name.replace('-',' ')
    name = name.replace('\xe2\x80\x94',' ')
    name = name.replace('\xe2\x80\x93',' ')
    
    name = name.replace('   ',' ')
    name = name.replace('  ',' ')
    #strip postfix
    for pf in postfix_list:
        if name.endswith(pf):
            name = name[:-1*len(pf)]
    name = name.strip()
    #do it again
    for pf in postfix_list:
        if name.endswith(pf):
            name = name[:-1*len(pf)]
    name = name.strip()
    #do it again
    for pf in postfix_list:
        if name.endswith(pf):
            name = name[:-1*len(pf)]
    name = name.strip()

    for alias in alias_list.keys():
        if alias in name:
            name = name.replace(alias, alias_list[alias])
    return name

if __name__ == "__main__":
    populate_ipo_underwriter()
    #reduce_list()
