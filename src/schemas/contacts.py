from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date
from typing import Optional


class ContactModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    additional_info: Optional[str] = None


class ContactResponse(BaseModel):
    id: int
    email: EmailStr
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class ContactUpdate(BaseModel):
    first_name: str = None
    last_name: str = None
    email: EmailStr = None
    phone_number: str = None
    birthday: date = None
    additional_info: Optional[str] = None