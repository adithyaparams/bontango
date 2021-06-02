from database import Base, SessionLocal

from services import articles as article_services
from services import google as google_services
from services import senders as sender_services
from services import users as user_services

from models import articles as article_models
from models import google as google_models
from models import senders as sender_models
from models import users as user_models

db = SessionLocal()
