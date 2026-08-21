from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid

class RegisterCompanyRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=150)
    tax_id: str = Field(..., min_length=3, max_length=50)
    owner_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=6)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
