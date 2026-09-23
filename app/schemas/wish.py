from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import datetime

class WishCreate(BaseModel):
    name: Optional[str] = None
    age_range: Optional[str] = None
    text: str

    @model_validator(mode="before")
    @classmethod
    def normalize_aliases(cls, data):
        if isinstance(data, dict):
            if not data.get("name"):
                data["name"] = data.get("visitor_name") or data.get("nama")
            if not data.get("age_range"):
                data["age_range"] = data.get("rentang_usia")
            if not data.get("text"):
                data["text"] = data.get("text_aspirasi") or data.get("aspirasi") or ""
        return data

class WishResponse(BaseModel):
    id: str
    name: Optional[str] = None
    age_range: Optional[str] = None
    text: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True