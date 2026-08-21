import uuid
from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.database import get_db
from src.shared.dependencies import get_current_tenant_id, get_current_user
from src.modules.users.models import User
from src.modules.products.models import Product
from src.modules.customers.models import Customer
from src.modules.sales.models import Sale, SaleItem, InventoryMovement
from src.modules.sales.schemas import SaleCreateRequest, SaleResponse

router = APIRouter(prefix="/sales", tags=["Sales"])

@router.get("", response_model=List[SaleResponse])
async def list_sales(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """HU-007: Consult sales history for active tenant."""
    stmt = (
        select(Sale)
        .options(selectinload(Sale.items))
        .where(Sale.tenant_id == tenant_id)
        .order_by(Sale.created_at.desc())
    )
    result = await db.execute(stmt)
    sales = result.scalars().all()

    # Populate customer_name and user_name
    response_list = []
    for sale in sales:
        customer = await db.get(Customer, sale.customer_id)
        seller = await db.get(User, sale.user_id)
        
        items_resp = []
        for item in sale.items:
            prod = await db.get(Product, item.product_id)
            items_resp.append({
                "id": item.id,
                "product_id": item.product_id,
                "product_name": prod.name if prod else "Producto",
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.subtotal
            })

        response_list.append({
            "id": sale.id,
            "tenant_id": sale.tenant_id,
            "customer_id": sale.customer_id,
            "customer_name": customer.name if customer else "Cliente",
            "user_id": sale.user_id,
            "user_name": seller.full_name if seller else "Vendedor",
            "total_amount": sale.total_amount,
            "status": sale.status,
            "created_at": sale.created_at,
            "items": items_resp
        })

    return response_list

@router.post("", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def register_sale(
    payload: SaleCreateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """HU-006: Register sale with row locking, atomic stock deduction, and inventory movement audit."""
    # Verify customer exists in tenant
    customer = await db.get(Customer, payload.customer_id)
    if not customer or customer.tenant_id != tenant_id:
        raise HTTPException(status_code=400, detail="El cliente seleccionado no existe en su empresa")

    product_ids = [item.product_id for item in payload.items]

    # 1. Row Lock (WITH FOR UPDATE) on products
    stmt = (
        select(Product)
        .where(Product.id.in_(product_ids), Product.tenant_id == tenant_id)
        .with_for_update()
    )
    result = await db.execute(stmt)
    products_db = {p.id: p for p in result.scalars().all()}

    # Verify all products exist and have sufficient stock
    for item in payload.items:
        if item.product_id not in products_db:
            raise HTTPException(
                status_code=400, 
                detail=f"El producto con ID {item.product_id} no pertenece a su empresa"
            )
        product = products_db[item.product_id]
        if product.status != "ACTIVE":
            raise HTTPException(
                status_code=400,
                detail=f"El producto '{product.name}' se encuentra inactivo y no puede venderse"
            )
        if product.current_stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para '{product.name}'. Disponible: {product.current_stock}, Solicitado: {item.quantity}"
            )

    # Calculate total and create Sale Header
    total_amount = Decimal("0.00")
    for item in payload.items:
        subtotal = Decimal(str(item.quantity)) * Decimal(str(item.unit_price))
        total_amount += subtotal

    sale = Sale(
        tenant_id=tenant_id,
        customer_id=customer.id,
        user_id=current_user.id,
        total_amount=total_amount,
        status="CONFIRMED"
    )
    db.add(sale)
    await db.flush()

    # Deduct stock and record items + inventory movements
    items_resp = []
    for item in payload.items:
        product = products_db[item.product_id]
        subtotal = Decimal(str(item.quantity)) * Decimal(str(item.unit_price))

        sale_item = SaleItem(
            sale_id=sale.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=subtotal
        )
        db.add(sale_item)

        stock_before = product.current_stock
        product.current_stock -= item.quantity
        stock_after = product.current_stock

        # Inmutable Audit Log
        movement = InventoryMovement(
            tenant_id=tenant_id,
            product_id=product.id,
            movement_type="SALE",
            quantity=-item.quantity,
            stock_before=stock_before,
            stock_after=stock_after,
            user_id=current_user.id,
            reference_id=sale.id
        )
        db.add(movement)

        items_resp.append({
            "id": uuid.uuid4(),
            "product_id": product.id,
            "product_name": product.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "subtotal": subtotal
        })

    await db.commit()
    await db.refresh(sale)

    return {
        "id": sale.id,
        "tenant_id": sale.tenant_id,
        "customer_id": customer.id,
        "customer_name": customer.name,
        "user_id": current_user.id,
        "user_name": current_user.full_name,
        "total_amount": sale.total_amount,
        "status": sale.status,
        "created_at": sale.created_at,
        "items": items_resp
    }
