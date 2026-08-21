import uuid
from typing import List, Callable
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database import get_db
from src.modules.users.models import User

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """Extract authenticated User from request state or return 401."""
    user_id = getattr(request.state, "user_id", None)
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida o sesión inválida"
        )
        
    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == tenant_id, User.status == "ACTIVE")
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo o no encontrado"
        )
    return user

async def get_current_tenant_id(current_user: User = Depends(get_current_user)) -> uuid.UUID:
    """Extract tenant_id from current authenticated user."""
    return current_user.tenant_id

def require_role(allowed_roles: List[str]) -> Callable:
    """Dependency guard verifying user role_id matches allowed roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role_id not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No posee permisos suficientes para acceder a este recurso"
            )
        return current_user
    return role_checker
