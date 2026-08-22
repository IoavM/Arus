import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient


async def _setup_tenant_with_sales(client: AsyncClient):
    """
    HU-012 fixture helper: registra una empresa, crea un producto con stock,
    un cliente adicional, y registra una venta a cada cliente.
    Retorna (headers, default_customer_id, other_customer_id).
    """
    reg = await client.post("/api/v1/auth/register-company", json={
        "company_name": "Filtros Ventas S.A.",
        "tax_id": "900555111",
        "owner_name": "Admin Filtros",
        "email": "admin@filtros.com",
        "password": "password123"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    prod_resp = await client.post("/api/v1/products", headers=headers, json={
        "sku": "PROD-FILTER-1",
        "name": "Café 500g",
        "sale_price": "8.00",
        "current_stock": 100
    })
    product_id = prod_resp.json()["id"]

    # Cliente por defecto "Consumidor Final" auto-creado en el registro
    cust_resp = await client.get("/api/v1/customers", headers=headers)
    default_customer_id = cust_resp.json()[0]["id"]

    other_resp = await client.post("/api/v1/customers", headers=headers, json={
        "name": "Cliente Frecuente",
        "tax_number": "1122334455"
    })
    other_customer_id = other_resp.json()["id"]

    # Una venta a cada cliente
    await client.post("/api/v1/sales", headers=headers, json={
        "customer_id": default_customer_id,
        "items": [{"product_id": product_id, "quantity": 2, "unit_price": "8.00"}]
    })
    await client.post("/api/v1/sales", headers=headers, json={
        "customer_id": other_customer_id,
        "items": [{"product_id": product_id, "quantity": 3, "unit_price": "8.00"}]
    })

    return headers, default_customer_id, other_customer_id


@pytest.mark.asyncio
async def test_filter_by_customer_returns_only_that_customer_sales(client: AsyncClient):
    """HU-012 Escenario 1: filtrar por cliente retorna únicamente sus ventas."""
    headers, default_customer_id, other_customer_id = await _setup_tenant_with_sales(client)

    resp = await client.get(
        "/api/v1/sales",
        headers=headers,
        params={"customer_id": other_customer_id}
    )
    assert resp.status_code == 200
    sales = resp.json()
    assert len(sales) == 1
    assert sales[0]["customer_id"] == other_customer_id
    assert sales[0]["customer_name"] == "Cliente Frecuente"


@pytest.mark.asyncio
async def test_filter_by_date_range(client: AsyncClient):
    """HU-012 Escenario 2: filtrar por rango de fechas incluye/excluye correctamente."""
    headers, _, _ = await _setup_tenant_with_sales(client)

    today = datetime.utcnow().date()

    # Rango que incluye hoy -> ambas ventas
    inside = await client.get("/api/v1/sales", headers=headers, params={
        "date_from": str(today),
        "date_to": str(today)
    })
    assert inside.status_code == 200
    assert len(inside.json()) == 2

    # Rango completamente en el pasado -> ninguna venta
    past = await client.get("/api/v1/sales", headers=headers, params={
        "date_from": str(today - timedelta(days=10)),
        "date_to": str(today - timedelta(days=5))
    })
    assert past.status_code == 200
    assert past.json() == []


@pytest.mark.asyncio
async def test_filter_combined_customer_and_date(client: AsyncClient):
    """HU-012 Escenario 3: cliente + rango de fechas se combinan como intersección."""
    headers, _, other_customer_id = await _setup_tenant_with_sales(client)

    today = datetime.utcnow().date()

    # Cliente correcto dentro del rango -> 1 venta
    match = await client.get("/api/v1/sales", headers=headers, params={
        "customer_id": other_customer_id,
        "date_from": str(today),
        "date_to": str(today)
    })
    assert match.status_code == 200
    assert len(match.json()) == 1
    assert match.json()[0]["customer_id"] == other_customer_id

    # Cliente correcto pero fuera del rango -> intersección vacía
    no_match = await client.get("/api/v1/sales", headers=headers, params={
        "customer_id": other_customer_id,
        "date_from": str(today - timedelta(days=10)),
        "date_to": str(today - timedelta(days=5))
    })
    assert no_match.status_code == 200
    assert no_match.json() == []


@pytest.mark.asyncio
async def test_no_filters_preserves_existing_behaviour(client: AsyncClient):
    """HU-012 Escenario 4: sin filtros, comportamiento idéntico al actual (todas, orden descendente)."""
    headers, _, _ = await _setup_tenant_with_sales(client)

    resp = await client.get("/api/v1/sales", headers=headers)
    assert resp.status_code == 200
    sales = resp.json()
    assert len(sales) == 2

    # Orden descendente por fecha preservado (HU-007 sin cambios)
    dates = [s["created_at"] for s in sales]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.asyncio
async def test_filter_by_foreign_tenant_customer_returns_empty(client: AsyncClient):
    """HU-012 Escenario 5: un customer_id de otro tenant retorna lista vacía, nunca datos ni error."""
    headers_a, _, _ = await _setup_tenant_with_sales(client)

    # Segundo tenant independiente
    reg_b = await client.post("/api/v1/auth/register-company", json={
        "company_name": "Empresa Ajena",
        "tax_id": "900555222",
        "owner_name": "Admin Ajeno",
        "email": "admin@ajena.com",
        "password": "password123"
    })
    headers_b = {"Authorization": f"Bearer {reg_b.json()['access_token']}"}

    cust_b = await client.get("/api/v1/customers", headers=headers_b)
    foreign_customer_id = cust_b.json()[0]["id"]

    # Tenant A filtrando por un cliente del tenant B
    resp = await client.get(
        "/api/v1/sales",
        headers=headers_a,
        params={"customer_id": foreign_customer_id}
    )
    assert resp.status_code == 200
    assert resp.json() == []
