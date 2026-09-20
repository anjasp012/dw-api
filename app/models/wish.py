import uuid
from sqlalchemy import Column, String, Text, DateTime, func
from app.db.session import Base

class Wish(Base):
    __tablename__ = "wishes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    text = Column(Text, nullable=False)
    status = Column(String(20), default="approved")
    created_at = Column(DateTime(timezone=True), server_default=func.now())