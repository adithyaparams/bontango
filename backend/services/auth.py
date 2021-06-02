from models.users import User
from services.users import get_user_by_email
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import jwt
from config import key, jwt_alg

def authenticate_user(db: Session, email: str, password: str):
    user: User = get_user_by_email(db, email)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = timedelta(minutes=15)):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, key, algorithm=jwt_alg)
    return encoded_jwt