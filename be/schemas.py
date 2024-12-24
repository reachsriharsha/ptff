from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_orm = True

class WatchlistCreate(BaseModel):
    name: str
    stocks: str

class Watchlist(WatchlistCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_orm = True