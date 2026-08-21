import pytest
from httpx import AsyncClient
from src.security import create_access_token

@pytest.mark.asyncio
async def test_seller_forbidden_from_admin_endpoints(client: AsyncClient):
    # 1. Register tenant and admin
    payload = {
        "company_name": "Empresa Auth RBAC",
        "tax_id": "900888777",
        "owner_name": "Propietario Auth",
        "email": "owner_rbac@test.com",
        "password": "PasswordTest123!"
    }
    resp = await client.post("/api/v1/auth/register-company", json=payload)
    assert resp.status_code == 201
    tenant_id = resp.json()["user"]["tenant_id"]

    # 2. Create Seller user under same tenant
    seller_payload = {
        "full_name": "Vendedor RBAC",
        "email": "vendedor_rbac@test.com",
        "password": "PasswordTest123!",
        "role_id": "SELLER"
    }
    admin_token = resp.json()["access_token"]
    seller_resp = await client.post(
        "/api/v1/users",
        json=seller_payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert seller_resp.status_code == 201
    seller_id = seller_resp.json()["id"]

    # 3. Seller login to get Seller JWT
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "vendedor_rbac@test.com",
        "password": "PasswordTest123!"
    })
    assert login_resp.status_code == 200
    seller_token = login_resp.json()["access_token"]
    seller_headers = {"Authorization": f"Bearer {seller_token}"}

    # 4. Seller attempts to access /users (Admin Only) -> 403 Forbidden
    users_resp = await client.get("/api/v1/users", headers=seller_headers)
    assert users_resp.status_code == 403
    assert "permisos suficientes" in users_resp.json()["detail"]

    # 5. Seller attempts to access /dashboard/summary (Admin Only) -> 403 Forbidden
    dash_resp = await client.get("/api/v1/dashboard/summary", headers=seller_headers)
    assert dash_resp.status_code == 403

    # 6. Seller can access /products (Allowed) -> 200 OK
    prod_resp = await client.get("/api/v1/products", headers=seller_headers)
    assert prod_resp.status_code == 200

@pytest.mark.asyncio
async def test_unauthenticated_request_rejected(client: AsyncClient):
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 401
