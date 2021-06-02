import services
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from services import articles as services

from schemas import articles as schemas
from schemas import users as user_schemas

from dependencies import get_current_user, get_db

router = APIRouter(
  prefix="/articles",
  tags=["articles"],
  responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.ArticleOut])
def get_all_articles_for_current_user(current_user: user_schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.get_articles_by_user(db, current_user.id)

@router.get("/{article_id}/body")
def get_article_body(article_id: int, current_user: user_schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.get_article_body(db, article_id=article_id)
