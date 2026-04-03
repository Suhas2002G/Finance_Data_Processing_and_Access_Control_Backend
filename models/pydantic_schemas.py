from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

class CreateUser(BaseModel):
    name : str = Field(min_length=2, max_length=72)
    email : EmailStr
    password: str = Field(min_length=6, max_length=72)

class LoginRequest(BaseModel):
    email : EmailStr
    password: str 


class TransactionCreate(BaseModel):
    amount: float = Field(gt=0)
    type: Literal["income", "expense"]
    category: str = Field(min_length=2, max_length=100)
    note: str | None = Field(default=None, max_length=500)
    date: datetime | None = None
    # user_id: int | None = None


class TransactionUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    type: Literal["income", "expense"] | None = None
    category: str | None = Field(default=None, min_length=2, max_length=100)
    note: str | None = Field(default=None, max_length=500)
    date: datetime | None = None
    # user_id: int | None = None

