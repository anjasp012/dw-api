from typing import Optional
from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserData(BaseModel):
    id: str
    username: str
    is_active: Optional[int] = 1

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    responseCode: str = "2000000"
    responseMessage: str = "Success"
    data: UserData