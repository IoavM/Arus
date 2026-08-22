from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class CategoryResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
