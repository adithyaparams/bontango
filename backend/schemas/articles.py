import datetime
from models.articles import Article
from pydantic import BaseModel

class Article(BaseModel):
    subject: str
    date: datetime.date
    author: str
    snippet: str

    class Config:
        orm_mode = True

class ArticleIn(Article):
    gmail_id: str
    sender_id: int
    user_id: int

class ArticleOut(Article):
    id: int