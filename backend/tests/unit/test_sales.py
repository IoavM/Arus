import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_sale_transaction_and_stock_deduction(client: AsyncClient):
    # 1. Register company
    reg = await client.post("/api/v1/auth/register-company", json={
        "company_name": "Ventas Test S.A.",
        "tax_id": "800111222",
        "owner_name": "Cajero Principal",
        "email": "cajero@test.com",
        "password": "password123"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Product
    prod_resp = await client.post("/api/v1/products", headers=headers, json={
        "sku": "PROD-SALES-1",
        "name": "Arroz 1kg",
        "sale_price": "3.50",
        "current_stock": 10
    })
    product_id = prod_resp.json()["id"]

    # 3. Get Default Customer (Consumidor Final)
    cust_resp = await client.get("/api/v1/customers", headers=headers)
    customer_id = cust_resp.json()[0]["id"]

    # 4. Process Sale of 3 units
    sale_resp = await client.post("/api/v1/sales", headers=headers, json={
        "customer_id": customer_id,
        "items": [
            {"product_id": product_id, "quantity": 3, "unit_price": "3.50"}
        ]
    })
    assert sale_resp.status_code == 201
    sale_data = sale_resp.json()
    assert float(sale_data["total_amount"]) == 10.50

    # 5. Verify product stock is now 7
    prod_check = await client.get("/api/v1/products", headers=headers)
    product_updated = [p for p in prod_check.json() if p["id"] == product_id][0]
    assert product_updated["current_stock"] == 7

@pytest.mark.asyncio
async def test_sale_rejection_insufficient_stock(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register-company", json={
        "company_name": "Ventas Test Insuficiente",
        "tax_id": "800111333",
        "owner_name": "Cajero 2",
        "email": "cajero2@test.com",
        "password": "password123"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    prod_resp = await client.post("/api/v1/products", headers=headers, json={
        "sku": "PROD-LIMITED",
        "name": "Aceite 1L",
        "sale_price": "10.00",
        "current_stock": 2
    })
    product_id = prod_resp.json()["id"]
    cust_resp = await client.get("/api/v1/customers", headers=headers)
    customer_id = cust_resp.json()[0]["id"]

    # Attempt to sell 5 units when only 2 available
    sale_resp = await client.post("/api/v1/sales", headers=headers, json={
        "customer_id": customer_id,
        "items": [
            {"product_id": product_id, "quantity": 5, "unit_price": "10.00"}
        ]
    })
    assert sale_resp.status_code == 400
    assert "Stock insuficiente" in sale_resp.json()["detail"]
