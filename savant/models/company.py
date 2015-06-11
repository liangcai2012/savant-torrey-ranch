from savant.models.setup import Base

# mapped classes are now created with names by default
# matching that of the table name.
class Company(Base):
    __tablename__ = 'company'

