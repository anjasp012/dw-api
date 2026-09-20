from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WishCreate(BaseModel):
    text: str

class WishResponse(BaseModel):
    id: str
    text: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True