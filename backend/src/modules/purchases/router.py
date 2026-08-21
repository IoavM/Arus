import uuid
from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.database import get_db
from src.shared.dependencies import get_current_tenant_id, get_current_user
from src.modules.users.models import User
from src.modules.products.models import Product
from src.modules.purchases.models import Purchase, PurchaseItem
from src.modules.sales.models import InventoryMovement
from src.modules.purchases.schemas import PurchaseCreateRequest, PurchaseResponse

router = APIRouter(prefix="/purchases", tags=["Purchases"])

@router.post("", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
async def register_purchase(
    payload: PurchaseCreateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """HU-008: Register a purchase and atomically increase product stock."""
    product_ids = [item.product_id for item in payload.items]
    
    # 1. Lock requested product rows
    stmt = (
        select(Product)
        .where(Product.id.in_(product_ids), Product.tenant_id == tenant_id)
        .with_for_update()
    )
    result = await db.execute(stmt)
    products_db = {p.id: p for p in result.scalars().all()}

    # Verify all products exist in tenant
    for item in payload.items:
        if item.product_id not in products_db:
            raise HTTPException(
                status_code=400, 
                detail=f"El producto con ID {item.product_id} no existe o no pertenece a su empresa"
            )

    # Calculate total and create Purchase Header
    total_amount = Decimal("0.00")
    for item in payload.items:
        subtotal = Decimal(str(item.quantity)) * Decimal(str(item.unit_cost))
        total_amount += subtotal

    purchase = Purchase(
        tenant_id=tenant_id,
        user_id=current_user.id,
        total_amount=total_amount
    )
    db.add(purchase)
    await db.flush()

    # Create Items and Update Stock Atomically
    for item in payload.items:
        product = products_db[item.product_id]
        subtotal = Decimal(str(item.quantity)) * Decimal(str(item.unit_cost))
        
        purchase_item = PurchaseItem(
            purchase_id=purchase.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_cost=item.unit_cost,
            subtotal=subtotal
        )
        db.add(purchase_item)

        stock_before = product.current_stock
        product.current_stock += item.quantity
        stock_after = product.current_stock

        # Log Inventory Movement
        movement = InventoryMovement(
            tenant_id=tenant_id,
            product_id=product.id,
            movement_type="PURCHASE",
            quantity=item.quantity,
            stock_before=stock_before,
            stock_after=stock_after,
            user_id=current_user.id,
            reference_id=purchase.id
        )
        db.add(movement)

    await db.commit()
    await db.refresh(purchase)

    # Re-query purchase with eager-loaded items for response
    result_final = await db.execute(
        select(Purchase).options(selectinload(Purchase.items)).where(Purchase.id == purchase.id)
    )
    return result_final.scalars().first()
