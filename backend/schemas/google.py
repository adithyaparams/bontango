from pydantic import BaseModel
from typing import List, Optional

class Account(BaseModel):
    email: str

    class Config:
        orm_mode = True

class AccountCreate(Account):
    client_id: str
    client_secret: str
    refresh_token: Optional[str] = None
    token: str
    token_uri: str

class AccountOut(Account):
    id: int