from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
import uuid
from datetime import datetime

class SaleItemRequest(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)

class SaleCreateRequest(BaseModel):
    customer_id: uuid.UUID
    items: List[SaleItemRequest] = Field(..., min_items=1)

class SaleItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: Optional[str] = None
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True

class SaleResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    customer_id: uuid.UUID
    customer_name: Optional[str] = None
    user_id: uuid.UUID
    user_name: Optional[str] = None
    total_amount: Decimal
    status: str
    created_at: datetime
    items: List[SaleItemResponse]

    class Config:
        from_attributes = True
