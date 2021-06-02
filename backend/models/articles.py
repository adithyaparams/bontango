from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from database import Base

class Article(Base):
    subject = Column(String)
    date = Column(DateTime)
    author = Column(String)
    snippet = Column(String)
    unread = Column(Boolean, default=True)
    gmail_id = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"))
    sender_id = Column(Integer, ForeignKey("sender.id"))

    user = relationship("User", back_populates="articles")
    sender = relationship("Sender", back_populates="articles")