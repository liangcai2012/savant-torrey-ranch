from savant.config import settings, db_settings
import mongoengine

mongoengine.connect(settings.MONGODB_NAME, host=settings.MONGODB_URI)
