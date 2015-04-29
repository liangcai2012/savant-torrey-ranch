import sqlalchemy
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from savant.config import settings


class SessionFactory(sessionmaker):
    """
    Session factory that configures the engine lazily at first use with the
    current settings.DATABASE_URI.
    """
    def __call__(self, **local_kw):
        if self.kw['bind'] is None and 'bind' not in local_kw:
            self.kw['bind'] = create_engine()
        return super(SessionFactory, self).__call__(**local_kw)


def create_engine():
    """
    Create an SQLAlchemy connection engine from the current configuration.
    """
    url = make_url(settings.DATABASE_URI)
    options = {}

    if settings.DEBUG:
        options.update(echo=True)

    if url.drivername == 'sqlite' and url.database in (None, '', ':memory:'):
        options.update(
            connect_args={'check_some_thread':False},
            poolclass=StaticPool)
        
        engine = sqlalchemy.create_engine(url, **options)

        Base.metadata.create_all(engine)
        return engine
    else:
        return sqlalchemy.create_engine(url, **options)


# Sessions are automatically created when needed and are scoped by thread
session_factory = SessionFactory()
session = scoped_session(session_factory)


# Declarative base class for our models
Base = declarative_base()
Base.query = session.query_property()
