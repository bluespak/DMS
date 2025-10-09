from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class MessageCreate(BaseModel):
    recipient_email: EmailStr
    subject: str
    body: str


class MessageResponse(BaseModel):
    id: int
    recipient_email: str
    subject: str
    body: str
    is_sent: bool
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SwitchCreate(BaseModel):
    name: str
    check_in_interval_days: int
    messages: List[MessageCreate]


class SwitchUpdate(BaseModel):
    name: Optional[str] = None
    check_in_interval_days: Optional[int] = None
    is_active: Optional[bool] = None


class SwitchResponse(BaseModel):
    id: int
    name: str
    check_in_interval_days: int
    last_check_in: datetime
    is_active: bool
    is_triggered: bool
    triggered_at: Optional[datetime]
    created_at: datetime
    messages: List[MessageResponse]

    class Config:
        from_attributes = True
