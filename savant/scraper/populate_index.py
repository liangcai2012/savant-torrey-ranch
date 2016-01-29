import savant.db
from savant.db import session
from savant.config import settings
from savant.db.models import MarketIndex 

def insert_index(symbol, name):
    try:
        MarketIndex.__table__.create(bind = savant.db.create_engine())
    except:
        savant.db.session.rollback()


    rec = {"symbol": symbol, "name": name} 
    mi= MarketIndex(**rec)
    savant.db.session.add(mi)
    try:
        savant.db.session.commit()
        print symbol, "added to index table"
    except:
        savant.db.session.rollback()
        print symbol, "cannot add index. It is added already"



if __name__ == "__main__":
    insert_index("^DJI", "Dow Jones Industrial Average")

