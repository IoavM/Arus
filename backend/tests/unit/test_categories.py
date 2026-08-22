import pytest
from httpx import AsyncClient


async def _register(client: AsyncClient, company: str, tax_id: str, email: str) -> dict:
    """Register a company and return its auth headers."""
    reg = await client.post("/api/v1/auth/register-company", json={
        "company_name": company,
        "tax_id": tax_id,
        "owner_name": "Admin",
        "email": email,
        "password": "password123"
    })
    assert reg.status_code == 201
    return {"Authorization": f"Bearer {reg.json()['access_token']}"}


@pytest.mark.asyncio
async def test_create_category_persists(client: AsyncClient):
    """HU-013 Scenario 1: creating a category stores it for the tenant."""
    headers = await _register(client, "Categorias Test S.A.", "900500001", "cat1@test.com")

    resp = await client.post("/api/v1/categories", headers=headers, json={"name": "Bebidas"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Bebidas"
    assert data["id"] and data["tenant_id"] and data["created_at"]


@pytest.mark.asyncio
async def test_list_categories_returns_only_active_tenant(client: AsyncClient):
    """HU-013 Scenario 2 + multi-tenant isolation on listing."""
    headers_a = await _register(client, "Empresa Cat A", "900500002", "cata@test.com")
    headers_b = await _register(client, "Empresa Cat B", "900500003", "catb@test.com")

    await client.post("/api/v1/categories", headers=headers_a, json={"name": "Exclusiva A"})

    list_a = await client.get("/api/v1/categories", headers=headers_a)
    assert list_a.status_code == 200
    assert "Exclusiva A" in [c["name"] for c in list_a.json()]

    # Company B must never see company A categories
    list_b = await client.get("/api/v1/categories", headers=headers_b)
    assert list_b.status_code == 200
    assert "Exclusiva A" not in [c["name"] for c in list_b.json()]


@pytest.mark.asyncio
async def test_associate_product_to_category(client: AsyncClient):
    """HU-013 Scenario 3: product keeps its category and it shows up on GET /products."""
    headers = await _register(client, "Empresa Asocia", "900500004", "asocia@test.com")

    cat_id = (await client.post("/api/v1/categories", headers=headers, json={"name": "Lacteos"})).json()["id"]

    prod = await client.post("/api/v1/products", headers=headers, json={
        "sku": "SKU-CAT-1",
        "name": "Leche Entera 1L",
        "sale_price": "4.20",
        "current_stock": 25,
        "category_id": cat_id
    })
    assert prod.status_code == 201
    assert prod.json()["category_id"] == cat_id

    listing = await client.get("/api/v1/products", headers=headers)
    product = [p for p in listing.json() if p["sku"] == "SKU-CAT-1"][0]
    assert product["category_id"] == cat_id


@pytest.mark.asyncio
async def test_product_without_category_still_works(client: AsyncClient):
    """HU-013 Scenario 4: category is fully optional on create and update."""
    headers = await _register(client, "Empresa Sin Cat", "900500005", "sincat@test.com")

    prod = await client.post("/api/v1/products", headers=headers, json={
        "sku": "SKU-SIN-CAT",
        "name": "Producto Sin Categoria",
        "sale_price": "9.99",
        "current_stock": 5
    })
    assert prod.status_code == 201
    assert prod.json()["category_id"] is None
    product_id = prod.json()["id"]

    # Updating without category_id keeps working exactly as before
    # min_stock es obligatorio en PUT desde HU-011 (contracts/endpoints.md); se
    # envia explicitamente para aislar lo que este test valida: que category_id
    # sigue siendo opcional.
    upd = await client.put(f"/api/v1/products/{product_id}", headers=headers, json={
        "name": "Producto Sin Categoria Editado",
        "sale_price": "10.50",
        "min_stock": 0
    })
    assert upd.status_code == 200
    assert upd.json()["category_id"] is None
    assert upd.json()["name"] == "Producto Sin Categoria Editado"


@pytest.mark.asyncio
async def test_duplicate_category_name_rejected(client: AsyncClient):
    """HU-013 Scenario 5: duplicate name within the same tenant is rejected with 400."""
    headers = await _register(client, "Empresa Duplicada", "900500006", "dup@test.com")

    first = await client.post("/api/v1/categories", headers=headers, json={"name": "Snacks"})
    assert first.status_code == 201

    second = await client.post("/api/v1/categories", headers=headers, json={"name": "Snacks"})
    assert second.status_code == 400
    assert "nombre" in second.json()["detail"].lower()


@pytest.mark.asyncio
async def test_cannot_associate_category_from_other_tenant(client: AsyncClient):
    """HU-013 Scenario 6: cross-tenant category association is rejected with 400."""
    headers_a = await _register(client, "Empresa Cross A", "900500007", "crossa@test.com")
    headers_b = await _register(client, "Empresa Cross B", "900500008", "crossb@test.com")

    # Same name allowed in a different tenant (uniqueness is per tenant)
    cat_a = await client.post("/api/v1/categories", headers=headers_a, json={"name": "Compartida"})
    cat_b = await client.post("/api/v1/categories", headers=headers_b, json={"name": "Compartida"})
    assert cat_a.status_code == 201
    assert cat_b.status_code == 201
    cat_a_id = cat_a.json()["id"]

    # Company B tries to use company A category on create
    prod = await client.post("/api/v1/products", headers=headers_b, json={
        "sku": "SKU-CROSS",
        "name": "Producto Cruzado",
        "sale_price": "1.00",
        "current_stock": 1,
        "category_id": cat_a_id
    })
    assert prod.status_code == 400

    # ... and on update
    own = await client.post("/api/v1/products", headers=headers_b, json={
        "sku": "SKU-PROPIO-B",
        "name": "Producto Propio B",
        "sale_price": "2.00",
        "current_stock": 3
    })
    own_id = own.json()["id"]

    upd = await client.put(f"/api/v1/products/{own_id}", headers=headers_b, json={
        "name": "Producto Propio B",
        "sale_price": "2.00",
        "min_stock": 0,
        "category_id": cat_a_id
    })
    assert upd.status_code == 400
