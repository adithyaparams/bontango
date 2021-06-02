from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from services import senders as services
from services import articles as article_services
from schemas import senders as schemas
from schemas import users as user_schemas
from schemas import articles as article_schemas

from dependencies import get_current_user, get_db

router = APIRouter(
  prefix="/senders",
  tags=["senders"],
  responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.SenderOut])
def get_all_senders_for_current_user(selected: bool = False, keyword: Optional[str] = "", skip: Optional[int] = 0,
        current_user: user_schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if (selected):
        return services.get_selected_senders(db=db, user_id=current_user.id)
    else:
        return services.get_senders_by_keyword(keyword=keyword, db=db, user_id=current_user.id, skip=skip)

@router.put("/{sender_id}", response_model=schemas.SenderOut)
def toggle_sender_selected(sender_id: int, current_user: user_schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    sender = services.get_sender(db, sender_id)

    if (not sender.is_selected):
        if (article_services.get_articles_by_sender(db=db, sender_id=sender_id)):
            article_services.generate_articles(db=db, sender=sender, start_date=sender.updated_at)
        else:
            article_services.generate_articles(db=db, sender=sender)
    
    sender.is_selected = not sender.is_selected
    db.commit()
    db.refresh(sender)

    return sender

# @router.post("/{sender_id}/articles", response_model=article_schemas.ArticleOut)
# def generate_initial_articles(sender_id: int, current_user: user_schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
#     sender = services.get_sender(db, sender_id)

#     return article_services.generate_articles(db, sender)

@router.put("/{sender_id}/articles", response_model=article_schemas.ArticleOut)
def update_articles(sender_id: int, current_user: user_schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    sender = services.get_sender(db, sender_id)

    return article_services.generate_articles(db, sender, sender.updated_at)

@router.get("/{sender_id}/articles", response_model=List[article_schemas.ArticleOut])
def get_all_articles_by_sender(sender_id: int, current_user: user_schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return article_services.get_articles_by_sender(db, sender_id)