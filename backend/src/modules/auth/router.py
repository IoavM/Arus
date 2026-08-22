from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database import get_db
from src.security import get_password_hash, verify_password, create_access_token
from src.modules.auth.models import Tenant
from src.modules.users.models import User, Role
from src.modules.customers.models import Customer
from src.modules.auth.schemas import RegisterCompanyRequest, LoginRequest, TokenResponse, ChangePasswordRequest
from src.shared.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register-company", status_code=status.HTTP_201_CREATED)
async def register_company(payload: RegisterCompanyRequest, db: AsyncSession = Depends(get_db)):
    """HU-001: Register company (Tenant) and owner user as ADMIN."""
    # Check if tax_id already exists
    existing_tenant = await db.execute(select(Tenant).where(Tenant.tax_id == payload.tax_id))
    if existing_tenant.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una empresa registrada con ese NIT / Identificación fiscal"
        )
        
    # Check if roles exist, if not seed them
    role_admin = await db.get(Role, "ADMIN")
    if not role_admin:
        db.add(Role(id="ADMIN", name="Administrador", description="Acceso total"))
        db.add(Role(id="SELLER", name="Vendedor", description="Operaciones comerciales"))
        await db.flush()

    # Create new Tenant
    new_tenant = Tenant(name=payload.company_name, tax_id=payload.tax_id)
    db.add(new_tenant)
    await db.flush()

    # Check email duplicate globally or per tenant
    existing_user = await db.execute(select(User).where(User.email == payload.email))
    if existing_user.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya se encuentra registrado"
        )

    # Create Owner User (Admin)
    owner = User(
        tenant_id=new_tenant.id,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        full_name=payload.owner_name,
        role_id="ADMIN",
        status="ACTIVE"
    )
    db.add(owner)

    # Auto-seed default customer "Consumidor Final" for this tenant
    default_customer = Customer(
        tenant_id=new_tenant.id,
        name="Consumidor Final",
        tax_number="222222222222",
        is_default=True,
        status="ACTIVE"
    )
    db.add(default_customer)

    await db.commit()
    await db.refresh(owner)

    # Generate JWT token
    token = create_access_token({
        "sub": str(owner.id),
        "tenant_id": str(new_tenant.id),
        "role_id": owner.role_id
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(owner.id),
            "tenant_id": str(new_tenant.id),
            "email": owner.email,
            "full_name": owner.full_name,
            "role_id": owner.role_id,
            "company_name": new_tenant.name
        }
    }

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """HU-002: Authenticate user and return JWT access token."""
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalars().first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos"
        )

    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Su cuenta de usuario se encuentra inactiva. Contacte al administrador."
        )

    # Fetch tenant info
    tenant = await db.get(Tenant, user.tenant_id)

    token = create_access_token({
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "role_id": user.role_id
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "tenant_id": str(user.tenant_id),
            "email": user.email,
            "full_name": user.full_name,
            "role_id": user.role_id,
            "company_name": tenant.name if tenant else ""
        }
    }

@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """HU-014: Change current user's password."""
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )

    current_user.password_hash = get_password_hash(payload.new_password)
    await db.commit()
    return {"message": "Contraseña actualizada correctamente"}

