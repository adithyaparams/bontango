from sqlalchemy.orm.session import Session
from database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import jwt
from config import key, jwt_alg
from schemas import auth as auth_schemas
from services import users as users_services

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, key, algorithms=[jwt_alg])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = auth_schemas.TokenData(user_id=user_id)
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = users_services.get_user(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user