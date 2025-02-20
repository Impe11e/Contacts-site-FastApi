from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

class ContactBase(BaseModel):
    name: str = Field(max_length=50)
    surname: str = Field(max_length=150)
    email: EmailStr
    phone: PhoneNumber

    class Config:
        orm_mode = True

class ContactModel(ContactBase):
    birthday: Optional[datetime] = Field(None, description="Contact's birthday on... Day-Month-Year")
    description: Optional[str] = Field(None, max_length=255, description="Your contact's info")


class ContactUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    surname: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthday: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=255)

class ContactResponse(ContactBase):
    id: int
