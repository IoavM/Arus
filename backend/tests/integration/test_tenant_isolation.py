import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_multi_tenant_isolation(client: AsyncClient):
    # 1. Register Company A
    reg_a = await client.post("/api/v1/auth/register-company", json={
        "company_name": "Empresa A",
        "tax_id": "900000001",
        "owner_name": "Admin A",
        "email": "admin@empresaa.com",
        "password": "password123"
    })
    token_a = reg_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Register Company B
    reg_b = await client.post("/api/v1/auth/register-company", json={
        "company_name": "Empresa B",
        "tax_id": "900000002",
        "owner_name": "Admin B",
        "email": "admin@empresab.com",
        "password": "password123"
    })
    token_b = reg_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. Create Product in Company A
    await client.post("/api/v1/products", headers=headers_a, json={
        "sku": "SKU-EXCLUSIVO-A",
        "name": "Producto Secreto A",
        "sale_price": "50.00",
        "current_stock": 100
    })

    # 4. Fetch Products using Company B token
    products_b = await client.get("/api/v1/products", headers=headers_b)
    assert products_b.status_code == 200
    prods_b_list = products_b.json()
    
    # 5. Verify Company B sees ZERO products from Company A
    skus_b = [p["sku"] for p in prods_b_list]
    assert "SKU-EXCLUSIVO-A" not in skus_b
