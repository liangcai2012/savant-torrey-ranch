from savant.config import settings, db_settings
from savant.models.setup import Base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import sessionmaker
import mongoengine

mongoengine.connect(settings.MONGODB_NAME, host=settings.MONGODB_URI)


from savant.models.company import Company
from savant.models.ipo import IPO

# engine, suppose it has two tables 'user' and 'address' set up
engine = create_engine(settings.DATABASE_URI)

# reflect the tables
Base.prepare(engine, reflect=True)

