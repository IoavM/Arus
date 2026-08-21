import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_company_success(client: AsyncClient):
    payload = {
        "company_name": "Empresa Test Alfa",
        "tax_id": "900999888",
        "owner_name": "Propietario Alfa",
        "email": "owner@alfa.com",
        "password": "securepassword123"
    }
    response = await client.post("/api/v1/auth/register-company", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role_id"] == "ADMIN"
    assert data["user"]["company_name"] == "Empresa Test Alfa"

@pytest.mark.asyncio
async def test_register_company_duplicate_tax_id(client: AsyncClient):
    payload1 = {
        "company_name": "Empresa Test Original",
        "tax_id": "900777666",
        "owner_name": "Propietario Original",
        "email": "owner@original.com",
        "password": "securepassword123"
    }
    await client.post("/api/v1/auth/register-company", json=payload1)

    payload2 = {
        "company_name": "Empresa Test Beta",
        "tax_id": "900777666",  # Duplicate tax_id
        "owner_name": "Propietario Beta",
        "email": "owner@beta.com",
        "password": "securepassword123"
    }
    response = await client.post("/api/v1/auth/register-company", json=payload2)
    assert response.status_code == 400
    assert "NIT" in response.json()["detail"] or "fiscal" in response.json()["detail"]

