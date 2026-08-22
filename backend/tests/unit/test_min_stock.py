import pytest
from httpx import AsyncClient


async def _register_and_get_headers(client: AsyncClient, tax_id: str, email: str) -> dict:
    """Registra una empresa nueva y devuelve los headers autenticados."""
    reg = await client.post("/api/v1/auth/register-company", json={
        "company_name": "Stock Minimo S.A.",
        "tax_id": tax_id,
        "owner_name": "Administrador Inventario",
        "email": email,
        "password": "password123"
    })
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_min_stock_defaults_to_zero_when_omitted(client: AsyncClient):
    """HU-011: crear producto sin especificar min_stock persiste 0 por defecto."""
    headers = await _register_and_get_headers(client, "900111001", "minstock1@test.com")

    resp = await client.post("/api/v1/products", headers=headers, json={
        "sku": "PROD-MIN-DEFAULT",
        "name": "Panela 500g",
        "sale_price": "2.50",
        "current_stock": 20
    })
    assert resp.status_code == 201
    assert resp.json()["min_stock"] == 0


@pytest.mark.asyncio
async def test_min_stock_persists_on_create(client: AsyncClient):
    """HU-011: crear producto con min_stock=10 y consultarlo conserva el valor."""
    headers = await _register_and_get_headers(client, "900111002", "minstock2@test.com")

    create_resp = await client.post("/api/v1/products", headers=headers, json={
        "sku": "PROD-MIN-10",
        "name": "Arroz 1kg",
        "sale_price": "3.50",
        "current_stock": 25,
        "min_stock": 10
    })
    assert create_resp.status_code == 201
    product_id = create_resp.json()["id"]
    assert create_resp.json()["min_stock"] == 10

    list_resp = await client.get("/api/v1/products", headers=headers)
    assert list_resp.status_code == 200
    product = [p for p in list_resp.json() if p["id"] == product_id][0]
    assert product["min_stock"] == 10


@pytest.mark.asyncio
async def test_min_stock_updated_via_put(client: AsyncClient):
    """HU-011: actualizar min_stock vía PUT refleja el nuevo valor."""
    headers = await _register_and_get_headers(client, "900111003", "minstock3@test.com")

    create_resp = await client.post("/api/v1/products", headers=headers, json={
        "sku": "PROD-MIN-UPDATE",
        "name": "Aceite 1L",
        "sale_price": "10.00",
        "current_stock": 30,
        "min_stock": 5
    })
    product_id = create_resp.json()["id"]

    update_resp = await client.put(f"/api/v1/products/{product_id}", headers=headers, json={
        "name": "Aceite 1L",
        "description": "Aceite vegetal",
        "sale_price": "10.00",
        "min_stock": 12
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["min_stock"] == 12

    list_resp = await client.get("/api/v1/products", headers=headers)
    product = [p for p in list_resp.json() if p["id"] == product_id][0]
    assert product["min_stock"] == 12


@pytest.mark.asyncio
async def test_low_stock_is_identifiable_from_products_listing(client: AsyncClient):
    """HU-011: GET /products expone los datos para que el frontend calcule "Stock bajo"."""
    headers = await _register_and_get_headers(client, "900111004", "minstock4@test.com")

    low_resp = await client.post("/api/v1/products", headers=headers, json={
        "sku": "PROD-LOW",
        "name": "Azucar 1kg",
        "sale_price": "4.00",
        "current_stock": 5,
        "min_stock": 10
    })
    low_id = low_resp.json()["id"]

    ok_resp = await client.post("/api/v1/products", headers=headers, json={
        "sku": "PROD-OK",
        "name": "Sal 1kg",
        "sale_price": "1.50",
        "current_stock": 40,
        "min_stock": 10
    })
    ok_id = ok_resp.json()["id"]

    listing = (await client.get("/api/v1/products", headers=headers)).json()
    low_product = [p for p in listing if p["id"] == low_id][0]
    ok_product = [p for p in listing if p["id"] == ok_id][0]

    assert low_product["current_stock"] < low_product["min_stock"]
    assert not (ok_product["current_stock"] < ok_product["min_stock"])

    # Subir el stock por encima del umbral hace desaparecer la condición de "Stock bajo"
    await client.put(f"/api/v1/products/{low_id}", headers=headers, json={
        "name": "Azucar 1kg",
        "description": None,
        "sale_price": "4.00",
        "min_stock": 3
    })
    listing = (await client.get("/api/v1/products", headers=headers)).json()
    low_product = [p for p in listing if p["id"] == low_id][0]
    assert not (low_product["current_stock"] < low_product["min_stock"])


@pytest.mark.asyncio
async def test_negative_min_stock_is_rejected(client: AsyncClient):
    """HU-011: min_stock negativo es rechazado con HTTP 422 (validación ge=0)."""
    headers = await _register_and_get_headers(client, "900111005", "minstock5@test.com")

    create_resp = await client.post("/api/v1/products", headers=headers, json={
        "sku": "PROD-MIN-NEG",
        "name": "Harina 1kg",
        "sale_price": "3.00",
        "current_stock": 10,
        "min_stock": -1
    })
    assert create_resp.status_code == 422

    valid_resp = await client.post("/api/v1/products", headers=headers, json={
        "sku": "PROD-MIN-NEG-OK",
        "name": "Harina 1kg",
        "sale_price": "3.00",
        "current_stock": 10,
        "min_stock": 4
    })
    product_id = valid_resp.json()["id"]

    update_resp = await client.put(f"/api/v1/products/{product_id}", headers=headers, json={
        "name": "Harina 1kg",
        "description": None,
        "sale_price": "3.00",
        "min_stock": -5
    })
    assert update_resp.status_code == 422


@pytest.mark.asyncio
async def test_sale_is_not_blocked_by_min_stock(client: AsyncClient):
    """HU-011: min_stock es informativo — no bloquea ninguna venta (exclusión explícita del spec)."""
    headers = await _register_and_get_headers(client, "900111006", "minstock6@test.com")

    prod_resp = await client.post("/api/v1/products", headers=headers, json={
        "sku": "PROD-MIN-SALE",
        "name": "Cafe 500g",
        "sale_price": "8.00",
        "current_stock": 5,
        "min_stock": 100
    })
    product_id = prod_resp.json()["id"]

    customer_id = (await client.get("/api/v1/customers", headers=headers)).json()[0]["id"]

    sale_resp = await client.post("/api/v1/sales", headers=headers, json={
        "customer_id": customer_id,
        "items": [
            {"product_id": product_id, "quantity": 3, "unit_price": "8.00"}
        ]
    })
    assert sale_resp.status_code == 201
