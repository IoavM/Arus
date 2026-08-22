import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database import get_db
from src.shared.dependencies import get_current_tenant_id, get_current_user
from src.modules.users.models import User
from src.modules.categories.models import Category
from src.modules.categories.schemas import (
    CategoryCreateRequest,
    CategoryResponse
)

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """HU-013: List product categories for active tenant."""
    stmt = select(Category).where(Category.tenant_id == tenant_id).order_by(Category.name.asc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """HU-013: Create a new product category (name unique per tenant)."""
    existing = await db.execute(
        select(Category).where(Category.tenant_id == tenant_id, Category.name == payload.name)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Ya existe una categoría registrada con este nombre")

    category = Category(
        tenant_id=tenant_id,
        name=payload.name
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category
