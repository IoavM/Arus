import uuid
from typing import Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.security import decode_access_token

class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware that inspects the Authorization header or session token
    and attaches the authenticated tenant_id to the request state.
    """
    async def dispatch(self, request: Request, call_next):
        request.state.tenant_id = None
        request.state.user_id = None
        request.state.role_id = None
        
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)
            if payload:
                tenant_id_str = payload.get("tenant_id")
                user_id_str = payload.get("sub")
                role_id = payload.get("role_id")
                
                if tenant_id_str:
                    try:
                        request.state.tenant_id = uuid.UUID(tenant_id_str)
                    except ValueError:
                        pass
                if user_id_str:
                    try:
                        request.state.user_id = uuid.UUID(user_id_str)
                    except ValueError:
                        pass
                request.state.role_id = role_id
                
        response = await call_next(request)
        return response
