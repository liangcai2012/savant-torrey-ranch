# from savant.models.setup import Base

# # mapped classes are now created with names by default
# # matching that of the table name.
# class Company(Base):
#     __tablename__ = 'company'



import mongoengine

class Company(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    symbol = mongoengine.StringField(max_length=10)
    market = mongoengine.StringField(max_length=30)
    ipo_price = mongoengine.DecimalField()
    shares = mongoengine.LongField()
    offer_amount = mongoengine.LongField()
    date_priced = mongoengine.DateTimeField()

    def clean(self):
        try:
            int(self.shares)
        except:
            del self.shares
        try:
            int(self.offer_amount)
        except:
            del self.offer_amount
        try:
            len(self.symbol)
        except:
            del self.symbol

    meta = {
        'indexes': [
            '-date_priced'
        ]
    }
