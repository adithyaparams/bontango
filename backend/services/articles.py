from datetime import datetime
from typing import Dict, List
from googleapiclient.discovery import Resource
from models import senders as sender_models
from sqlalchemy.orm import Session
from models import articles as models
from schemas import articles as schemas
from models import google as google_models
from services import google as google_services
import email.utils
import utils

def get_article(db: Session, article_id: int):
    return db.query(models.Article).filter(models.Article.id == article_id).first()

def get_articles_by_user(db: Session, user_id: int):
    return db.query(models.Article).filter(models.Article.user_id == user_id).all()

def get_articles_by_sender(db: Session, sender_id: int):
    return db.query(models.Article).filter(models.Article.sender_id == sender_id).all()

def get_article_body(db: Session, article_id: int, mime_type: str = 'text/html'):
    article = get_article(db, article_id)
    gmail = google_services.initialize_gmail(article.sender.account)
    
    payload = gmail.users().messages().get(userId='me', id=article.gmail_id, format='full').execute()['payload']
    
    if payload['mimeType'] == 'multipart/alternative':
        for part in payload['parts']:
            if part['mimeType'] == mime_type:
                return part['body']['data']

    return payload

def generate_articles(db: Session, sender: sender_models.Sender, start_date: datetime = datetime.min):
    #TODO: possibly very weak logic here
    account: google_models.Google = sender.account
    gmail: Resource = google_services.initialize_gmail(account)
    name, address = email.utils.parseaddr(sender.label)
    
    sender.updated_at = datetime.now()
    db.commit()

    messages: List[Dict]
    if (start_date == datetime.min):
        messages = gmail.users().messages().list(userId='me', q=f"from:{address}", maxResults=20).execute()['messages']
    else:
        results = gmail.users().messages().list(userId='me', q=f"from:{address}").execute()
        messages = results['messages']
        while 'nextPageToken' in results:
            results = gmail.users().messages().list(userId='me', q=f"from:{address}", pageToken=results['nextPageToken']).execute()
            messages.extend(results['messages'])


    created_articles: List[models.Article] = []
    for message in messages:
        latest_email = gmail.users().messages().get(userId='me', id=message['id'], format='metadata').execute()
        article_props = gmail_to_internal(latest_email)
        if (article_props['date'] > start_date):
            created_articles.append(
                create_article(
                    db=db,
                    article=schemas.ArticleIn.parse_obj({
                        **article_props,
                        'author': name,
                        'sender_id': sender.id,
                        'user_id': sender.user_id
                    })
                )
            )

    return created_articles

def create_article(db: Session, article: schemas.ArticleIn):
    db_article = models.Article(
        subject=article.subject,
        date=article.date,
        author=article.author,
        snippet=article.snippet,
        gmail_id=article.gmail_id,
        sender_id=article.sender_id,
        user_id=article.user_id,
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def gmail_to_internal(metadata: Dict):
    internal_dict = {}
    internal_dict['gmail_id'] = metadata['id']
    internal_dict['snippet'] = metadata['snippet']
    internal_dict['date'] = utils.epoch_to_date(metadata['internalDate'])

    for header in metadata['payload']['headers']:
        if header['name'] == 'Subject':
            internal_dict['subject'] = header['value']

    return internal_dict

def update_articles():
    pass

def load_full_article():
    pass