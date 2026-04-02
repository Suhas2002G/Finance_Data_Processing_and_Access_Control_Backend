from pydantic import BaseModel, EmailStr, Field

class CreateUser(BaseModel):
    name : str = Field(min_length=2, max_length=72)
    email : EmailStr
    password: str = Field(min_length=6, max_length=72)

class LoginRequest(BaseModel):
    email : EmailStr
    password: str 

