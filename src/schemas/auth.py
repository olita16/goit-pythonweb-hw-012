from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class UserModel(BaseModel):
    email: EmailStr
    password: str


class UserModelRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class User(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
class RequestResetPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    password: str

class ResetPasswordWithToken(BaseModel):
    token: str
    password: str