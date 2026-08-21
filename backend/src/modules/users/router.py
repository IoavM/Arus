import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database import get_db
from src.security import get_password_hash
from src.shared.dependencies import require_role, get_current_tenant_id
from src.modules.users.models import User
from src.modules.users.schemas import UserCreateRequest, UserStatusUpdateRequest, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=List[UserResponse])
async def list_users(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_admin: User = Depends(require_role(["ADMIN"])),
    db: AsyncSession = Depends(get_db)
):
    """HU-003: List all collaborators for the active tenant (Admin only)."""
    result = await db.execute(select(User).where(User.tenant_id == tenant_id).order_by(User.created_at.desc()))
    return result.scalars().all()

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_admin: User = Depends(require_role(["ADMIN"])),
    db: AsyncSession = Depends(get_db)
):
    """HU-003: Create new collaborator (Admin only)."""
    if payload.role_id not in ["ADMIN", "SELLER"]:
        raise HTTPException(status_code=400, detail="El rol asignado no es válido")

    # Check for duplicate email in tenant
    existing = await db.execute(select(User).where(User.tenant_id == tenant_id, User.email == payload.email))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Ya existe un colaborador con este correo electrónico")

    user = User(
        tenant_id=tenant_id,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        full_name=payload.full_name,
        role_id=payload.role_id,
        status="ACTIVE"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.patch("/{user_id}/status", response_model=UserResponse)
async def toggle_user_status(
    user_id: uuid.UUID,
    payload: UserStatusUpdateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_admin: User = Depends(require_role(["ADMIN"])),
    db: AsyncSession = Depends(get_db)
):
    """HU-003: Activate or Inactivate collaborator (Admin only)."""
    result = await db.execute(select(User).where(User.id == user_id, User.tenant_id == tenant_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="No puede inactivar su propio usuario administrador")

    user.status = payload.status
    await db.commit()
    await db.refresh(user)
    return user
