from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.database import engine
from src.middleware.tenant import TenantMiddleware

# Import routers
from src.modules.auth.router import router as auth_router
from src.modules.users.router import router as users_router
from src.modules.products.router import router as products_router
from src.modules.customers.router import router as customers_router
from src.modules.purchases.router import router as purchases_router
from src.modules.sales.router import router as sales_router
from src.modules.dashboard.router import router as dashboard_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Multi-Tenant Context Middleware
app.add_middleware(TenantMiddleware)

# Mount Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(products_router, prefix=settings.API_V1_STR)
app.include_router(customers_router, prefix=settings.API_V1_STR)
app.include_router(purchases_router, prefix=settings.API_V1_STR)
app.include_router(sales_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Arus ERP API Running", "version": settings.VERSION}
