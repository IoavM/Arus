from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import uuid

class CustomerCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    tax_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class CustomerUpdateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    tax_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class CustomerStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(ACTIVE|INACTIVE)$")

class CustomerResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    tax_number: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    is_default: bool
    status: str

    class Config:
        from_attributes = True
