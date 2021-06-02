from sqlalchemy import Column, String, Integer, ForeignKey
from database import Base

from sqlalchemy.orm import relationship

class Google(Base):
  email = Column(String, index=True, unique=True)
  client_id = Column(String)
  client_secret = Column(String)
  refresh_token = Column(String)
  token = Column(String)
  token_uri = Column(String)
  owner_id = Column(Integer, ForeignKey("user.id"))

  owner = relationship("User", back_populates="accounts")
  senders = relationship("Sender", back_populates="account")