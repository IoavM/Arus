import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from src.database import get_db
from src.shared.dependencies import get_current_tenant_id, get_current_user
from src.modules.users.models import User
from src.modules.customers.models import Customer
from src.modules.customers.schemas import (
    CustomerCreateRequest,
    CustomerUpdateRequest,
    CustomerStatusRequest,
    CustomerResponse
)

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("", response_model=List[CustomerResponse])
async def list_customers(
    query: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """HU-005: List and search customers for active tenant."""
    stmt = select(Customer).where(Customer.tenant_id == tenant_id)
    
    if status_filter:
        stmt = stmt.where(Customer.status == status_filter)
        
    if query:
        search_pattern = f"%{query}%"
        stmt = stmt.where(
            or_(
                Customer.name.ilike(search_pattern),
                Customer.tax_number.ilike(search_pattern)
            )
        )
        
    stmt = stmt.order_by(Customer.is_default.desc(), Customer.name.asc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """HU-005: Register a new customer."""
    customer = Customer(
        tenant_id=tenant_id,
        name=payload.name,
        tax_number=payload.tax_number,
        phone=payload.phone,
        email=payload.email,
        is_default=False,
        status="ACTIVE"
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: uuid.UUID,
    payload: CustomerUpdateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """HU-005: Update customer info."""
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id, Customer.tenant_id == tenant_id)
    )
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    customer.name = payload.name
    customer.tax_number = payload.tax_number
    customer.phone = payload.phone
    customer.email = payload.email
    await db.commit()
    await db.refresh(customer)
    return customer

@router.patch("/{customer_id}/status", response_model=CustomerResponse)
async def toggle_customer_status(
    customer_id: uuid.UUID,
    payload: CustomerStatusRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """HU-005: Inactivate customer (soft-delete)."""
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id, Customer.tenant_id == tenant_id)
    )
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    if customer.is_default:
        raise HTTPException(status_code=400, detail="No se puede inactivar el cliente por defecto Consumidor Final")

    customer.status = payload.status
    await db.commit()
    await db.refresh(customer)
    return customer
