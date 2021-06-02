from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from database import Base

class Sender(Base):
    label = Column(String)
    freq = Column(Integer)
    is_selected = Column(Boolean, default=False)
    account_id = Column(Integer, ForeignKey("google.id"))
    user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship("User")
    account = relationship("Google", back_populates="senders")
    articles = relationship("Article", back_populates="sender")