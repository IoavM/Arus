# Quickstart Validation Guide: Arus ERP Baseline

**Feature**: `001-initial-baseline`  
**Date**: 2026-08-20  
**Spec**: [spec.md](file:///c:/Users/ioavm/OneDrive/Escritorio/IOAV/Arus/specs/001-initial-baseline/spec.md)  
**Contracts**: [openapi.json](file:///c:/Users/ioavm/OneDrive/Escritorio/IOAV/Arus/specs/001-initial-baseline/contracts/openapi.json)

---

## 1. Local Environment Setup

### 1.1 Prerequisites
* Python 3.11+
* PostgreSQL 15+
* Node.js 18+ & npm

### 1.2 Environment Variables Configuration
Backend `.env` template:
```env
DATABASE_URL=postgresql+asyncpg://arus_user:arus_password@localhost:5432/arus_db
JWT_SECRET_KEY=super_secret_key_for_jwt_auth_baseline
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

Frontend `.env` template:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 2. Automated Test Suite Scenarios

### 2.1 Backend Tests Execution
```bash
# Run pytest contract & integration tests
pytest backend/tests -v
```

### 2.2 Core Validation Sequence (10 HUs End-to-End Flow)

1. **HU-001 (Register Company)**:
   - Request: `POST /api/v1/auth/register-company` with `company_name="Micronegocio Alfa"`, `tax_id="900123456"`, `email="dueno@alfa.com"`.
   - Expected Outcome: HTTP 201 Created. `tenant_id` and `user_id` created with `role_id="ADMIN"`.

2. **HU-002 (Login)**:
   - Request: `POST /api/v1/auth/login` with `email="dueno@alfa.com"`, `password="..."`.
   - Expected Outcome: HTTP 200 OK. Returns JWT token with tenant claims.

3. **HU-003 (Manage Users)**:
   - Request: `POST /api/v1/users` (Header: Bearer Admin token) creating collaborator `email="vendedor@alfa.com"` with `role_id="SELLER"`.
   - Expected Outcome: HTTP 201 Created. `vendedor@alfa.com` can log in but is blocked from `/users` and `/dashboard/summary` (returns HTTP 403).

4. **HU-004 (Manage Products)**:
   - Request: `POST /api/v1/products` creating `sku="PROD-001"`, `name="Harina 1kg"`, `sale_price=5.00`, `current_stock=100`.
   - Expected Outcome: HTTP 201 Created. Stock initialized at 100.

5. **HU-005 (Manage Customers)**:
   - Request: `POST /api/v1/customers` creating `name="Juan Pérez"`, `tax_number="12345678"`.
   - Expected Outcome: HTTP 201 Created. Default customer "Consumidor Final" is also auto-created.

6. **HU-008 (Register Purchase)**:
   - Request: `POST /api/v1/purchases` with item `product_id="[PROD-001 ID]"`, `quantity=50`, `unit_cost=3.50`.
   - Expected Outcome: HTTP 201 Created. Stock for `PROD-001` increases from 100 to 150.

7. **HU-006 (Register Sale)**:
   - Request: `POST /api/v1/sales` with item `product_id="[PROD-001 ID]"`, `quantity=20`, `unit_price=5.00`.
   - Expected Outcome: HTTP 201 Created. Stock for `PROD-001` decreases from 150 to 130 in an atomic transaction.

8. **HU-007 (Consult Sales)** & **HU-009 (Consult Inventory)**:
   - Request: `GET /api/v1/sales` and `GET /api/v1/products`.
   - Expected Outcome: Sales list shows sale of $100.00 total. Product stock shows exactly 130.

9. **HU-010 (Consult Business Summary)**:
   - Request: `GET /api/v1/dashboard/summary` (Admin token).
   - Expected Outcome: HTTP 200 OK. `total_sales_amount=100.00`, `total_sales_count=1`.

10. **Multi-Tenant Isolation Validation**:
    - Register a second company "Empresa Beta" (`HU-001`).
    - Attempt to fetch products of "Micronegocio Alfa" using Beta token.
    - Expected Outcome: HTTP 200 returning empty list for Beta or 404/403 for direct ID lookup. Zero leakage.
