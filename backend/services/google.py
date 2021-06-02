import googleapiclient.discovery
from config import API_SERVICE_NAME, API_VERSION, SCOPES
from typing import List
from sqlalchemy.orm import Session

from models import google as models
from schemas import google as schemas
import google.oauth2.credentials

def initialize_gmail(account: models.Google):
    credentials = google.oauth2.credentials.Credentials(
        token=account.token,
        refresh_token=account.refresh_token,
        token_uri=account.token_uri,
        client_id=account.client_id,
        client_secret=account.client_secret,
        scopes=SCOPES
    )

    gmail = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    return gmail

def get_account(db: Session, account_id: int):
    return db.query(models.Google).filter(models.Google.id == account_id).first()

def create_account(db: Session, account: schemas.AccountCreate):
    db_account = models.Google(
        email=account.email, 
        client_id=account.client_id, 
        client_secret=account.client_secret, 
        refresh_token=account.refresh_token, 
        token=account.token, 
        token_uri=account.token_uri)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account