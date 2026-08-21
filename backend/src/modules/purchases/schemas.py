from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
import uuid
from datetime import datetime

class PurchaseItemRequest(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0)
    unit_cost: Decimal = Field(..., ge=0)

class PurchaseCreateRequest(BaseModel):
    items: List[PurchaseItemRequest] = Field(..., min_items=1)

class PurchaseItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: Optional[str] = None
    quantity: int
    unit_cost: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True

class PurchaseResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    total_amount: Decimal
    created_at: datetime
    items: List[PurchaseItemResponse]

    class Config:
        from_attributes = True
