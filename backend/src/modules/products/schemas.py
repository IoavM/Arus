from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
import uuid

class ProductCreateRequest(BaseModel):
    sku: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    sale_price: Decimal = Field(..., ge=0)
    current_stock: int = Field(..., ge=0)

class ProductUpdateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    sale_price: Decimal = Field(..., ge=0)

class ProductStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(ACTIVE|INACTIVE)$")

class ProductResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    sku: str
    name: str
    description: Optional[str]
    sale_price: Decimal
    current_stock: int
    status: str

    class Config:
        from_attributes = True
