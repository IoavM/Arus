import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from src.database import get_db
from src.shared.dependencies import get_current_tenant_id, get_current_user
from src.modules.users.models import User
from src.modules.products.models import Product
from src.modules.categories.models import Category
from src.modules.products.schemas import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductStatusRequest,
    ProductResponse
)

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=List[ProductResponse])
async def list_products(
    query: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """HU-004 & HU-009: List and search catalog / inventory for active tenant."""
    stmt = select(Product).where(Product.tenant_id == tenant_id)
    
    if status_filter:
        stmt = stmt.where(Product.status == status_filter)
        
    if query:
        search_pattern = f"%{query}%"
        stmt = stmt.where(
            or_(
                Product.sku.ilike(search_pattern),
                Product.name.ilike(search_pattern)
            )
        )
        
    stmt = stmt.order_by(Product.name.asc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """HU-004: Create a new product in tenant catalog."""
    existing = await db.execute(
        select(Product).where(Product.tenant_id == tenant_id, Product.sku == payload.sku)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Ya existe un producto registrado con este código / SKU")

    # HU-013: verify category exists in tenant
    if payload.category_id:
        category = await db.get(Category, payload.category_id)
        if not category or category.tenant_id != tenant_id:
            raise HTTPException(status_code=400, detail="Categoría no válida para esta empresa")

    product = Product(
        tenant_id=tenant_id,
        sku=payload.sku,
        name=payload.name,
        description=payload.description,
        sale_price=payload.sale_price,
        current_stock=payload.current_stock,
        status="ACTIVE",
        category_id=payload.category_id
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: uuid.UUID,
    payload: ProductUpdateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """HU-004: Update product name, description, and price."""
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.tenant_id == tenant_id)
    )
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # HU-013: verify category exists in tenant
    if payload.category_id:
        category = await db.get(Category, payload.category_id)
        if not category or category.tenant_id != tenant_id:
            raise HTTPException(status_code=400, detail="Categoría no válida para esta empresa")

    product.name = payload.name
    product.description = payload.description
    product.sale_price = payload.sale_price
    product.category_id = payload.category_id
    await db.commit()
    await db.refresh(product)
    return product

@router.patch("/{product_id}/status", response_model=ProductResponse)
async def toggle_product_status(
    product_id: uuid.UUID,
    payload: ProductStatusRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """HU-004: Inactivate product (soft-delete) to preserve transactional history."""
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.tenant_id == tenant_id)
    )
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    product.status = payload.status
    await db.commit()
    await db.refresh(product)
    return product
