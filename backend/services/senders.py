from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import func
from typing import List, Dict

from models import senders as models
from models import google as google_models
from schemas import senders as schemas
from datetime import timedelta, datetime
from collections import defaultdict
from googleapiclient.discovery import Resource
import utils

def get_sender(db: Session, sender_id: int):
    return db.query(models.Sender).filter(models.Sender.id == sender_id).first()

def get_senders_by_account(db: Session, account_id: int):
    return db.query(models.Sender).filter(models.Sender.account_id == account_id).all()

def get_selected_senders(db: Session, user_id: int):
    return db.query(models.Sender).filter(models.Sender.user_id == user_id).filter(models.Sender.is_selected == True).all()

def get_sender_count_by_keyword(db: Session, keyword: str, user_id: int):
    return db.query(func.count(models.Sender.id)) \
        .filter(models.Sender.user_id == user_id) \
        .filter(models.Sender.is_selected == False) \
        .filter(models.Sender.label.like(f'%${keyword}%'))

def get_senders_by_keyword(db: Session, keyword: str, user_id: int, skip: int = 0, limit: int = 6):
    return db.query(models.Sender) \
        .filter(models.Sender.user_id == user_id) \
        .filter(models.Sender.is_selected == False) \
        .filter(models.Sender.label.like(f'%{keyword}%')) \
        .order_by(models.Sender.freq.desc()) \
        .offset(skip*6).limit(limit) \
        .all()

def locate_sender(metadata: List[dict]):
    for header in metadata:
        if header['name'] == 'From':
            return header['value']
    print("No sender found for: ", metadata)
    return None

def create_sender(db: Session, sender: schemas.SenderIn):
    db_sender = models.Sender(label=sender.label, freq=sender.freq, account_id=sender.account_id, user_id=sender.user_id)
    db.add(db_sender)
    db.commit()
    db.refresh(db_sender)
    return db_sender

def generate_senders(db: Session, gmail: Resource, account: google_models.Google, user_id: int, start_date: datetime = datetime.now() - timedelta(weeks=2)) -> int:
    page_token = None
    farthest_back = None
    sender_freq: Dict[str, int] = defaultdict(int)

    account.updated_at = datetime.now()
    db.commit()

    while farthest_back is None or farthest_back >= start_date:
        if page_token is None:
            request = gmail.users().messages().list(userId='me')
        else:
            request = gmail.users().messages().list(userId='me', pageToken=page_token)
        
        results = request.execute()
        page_token = results['nextPageToken']

        for message in results['messages']:
            latest_email = gmail.users().messages().get(userId='me', id=message['id'], format='metadata').execute()
            farthest_back = utils.epoch_to_date(latest_email['internalDate'])
            if farthest_back >= start_date:
                sender = locate_sender(latest_email['payload']['headers'])
                print(sender)
                sender_freq[sender] += 1

    for label, freq in sender_freq.items():
        print(label, freq)
        create_sender(
            db=db,
            sender=schemas.SenderIn.parse_obj({
                'label': label,
                'freq': freq,
                'account_id': account.id,
                'user_id': user_id
            })
        )

    return len(sender_freq)