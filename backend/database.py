from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from config import db_url
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, DateTime

class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    id =  Column(Integer, primary_key=True)

engine = create_engine(
    db_url, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base(cls=Base)

Hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")