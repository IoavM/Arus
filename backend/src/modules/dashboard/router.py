import uuid
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from src.database import get_db
from src.shared.dependencies import require_role, get_current_tenant_id
from src.modules.users.models import User
from src.modules.products.models import Product
from src.modules.customers.models import Customer
from src.modules.sales.models import Sale
from src.modules.dashboard.schemas import DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_admin: User = Depends(require_role(["ADMIN"])),
    db: AsyncSession = Depends(get_db)
):
    """HU-010: Executive metrics summary for tenant (Admin only)."""
    # Total sales amount and count
    sales_stmt = select(
        func.coalesce(func.sum(Sale.total_amount), 0),
        func.count(Sale.id)
    ).where(Sale.tenant_id == tenant_id, Sale.status == "CONFIRMED")
    sales_res = await db.execute(sales_stmt)
    total_sales_amount, total_sales_count = sales_res.first()

    # Active products count
    products_stmt = select(func.count(Product.id)).where(Product.tenant_id == tenant_id, Product.status == "ACTIVE")
    products_count = (await db.execute(products_stmt)).scalar() or 0

    # Active customers count
    customers_stmt = select(func.count(Customer.id)).where(Customer.tenant_id == tenant_id, Customer.status == "ACTIVE")
    customers_count = (await db.execute(customers_stmt)).scalar() or 0

    # Active users count
    users_stmt = select(func.count(User.id)).where(User.tenant_id == tenant_id, User.status == "ACTIVE")
    users_count = (await db.execute(users_stmt)).scalar() or 0

    return {
        "total_sales_amount": Decimal(str(total_sales_amount)),
        "total_sales_count": total_sales_count,
        "active_products_count": products_count,
        "active_customers_count": customers_count,
        "active_users_count": users_count
    }
