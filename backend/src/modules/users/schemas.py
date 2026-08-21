from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid

class UserCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role_id: str = Field(..., description="ADMIN or SELLER")

class UserStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(ACTIVE|INACTIVE)$")

class UserResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    full_name: str
    role_id: str
    status: str

    class Config:
        from_attributes = True
