from pydantic import BaseModel

class Sender(BaseModel):
    label: str
    freq: int

    class Config:
        orm_mode = True

class SenderIn(Sender):
    account_id: int
    user_id: int

class SenderOut(Sender):
    id: int