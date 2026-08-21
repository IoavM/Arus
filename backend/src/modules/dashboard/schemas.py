from pydantic import BaseModel
from decimal import Decimal

class DashboardSummaryResponse(BaseModel):
    total_sales_amount: Decimal
    total_sales_count: int
    active_products_count: int
    active_customers_count: int
    active_users_count: int
