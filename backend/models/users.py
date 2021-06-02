from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base, Hasher
from models import articles

class User(Base):
    email = Column(String, unique=True, index=True)
    password_hash = Column("password", String)
    is_active = Column(Boolean, default=True)

    accounts = relationship("Google", back_populates="owner")
    articles = relationship("Article", back_populates="user")

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = Hasher.hash(password)
    
    def verify_password(self, password): 
        return Hasher.verify(password, self.password_hash)