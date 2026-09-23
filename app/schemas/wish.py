from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import datetime

class WishCreate(BaseModel):
    name: Optional[str] = None
    age_range: Optional[str] = None
    text: str

    # Fallback aliases
    visitor_name: Optional[str] = None
    nama: Optional[str] = None
    rentang_usia: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_aliases(cls, data):
        if isinstance(data, dict):
            if not data.get("name"):
                data["name"] = data.get("visitor_name") or data.get("nama")
            if not data.get("age_range"):
                data["age_range"] = data.get("rentang_usia")
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