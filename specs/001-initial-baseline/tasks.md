# Implementation Tasks: Arus ERP Baseline

**Feature**: `001-initial-baseline`  
**Date**: 2026-08-20  
**Last Updated**: 2026-08-21  
**Spec**: [spec.md](file:///c:/Users/ioavm/OneDrive/Escritorio/IOAV/Arus/specs/001-initial-baseline/spec.md)  
**Plan**: [plan.md](file:///c:/Users/ioavm/OneDrive/Escritorio/IOAV/Arus/specs/001-initial-baseline/plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, basic structure setup, and automated test environment configuration.

- [x] T001 Create project directory structure for backend and frontend per implementation plan
- [x] T002 Initialize Python FastAPI backend with dependencies (`FastAPI`, `Pydantic`, `SQLAlchemy`, `asyncpg`, `Alembic`, `PyJWT`, `passlib`, `pytest`, `pytest-asyncio`, `httpx`) in `backend/pyproject.toml`
- [x] T003 [P] Initialize React Vite frontend with dependencies (`react`, `axios`, `react-router-dom`, `vitest`) in `frontend/package.json`
- [x] T004 [P] Configure environment variables and settings loader in `backend/src/config.py` and `frontend/.env`
- [x] T005_T [P] Setup automated test fixtures and in-memory database setup (`sqlite+aiosqlite:///:memory:`) in `backend/tests/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and security utilities that MUST be complete before ANY user story can be implemented.

- [x] T005 Setup SQLAlchemy async database engine & session maker in `backend/src/database.py`
- [x] T006 [P] Configure Alembic database migration environment in `backend/alembic/env.py`
- [x] T007 [P] Create base SQLAlchemy declarative model & TenantMixin in `backend/src/shared/models.py`
- [x] T008 [P] Implement password hashing (bcrypt) and JWT token utility functions in `backend/src/security.py`
- [x] T009 Implement multi-tenant context extraction middleware in `backend/src/middleware/tenant.py`
- [x] T010 [P] Implement common FastAPI dependency guards (`get_db`, `get_current_user`, `require_role`) in `backend/src/shared/dependencies.py`
- [x] T011 [P] Setup frontend Axios HTTP client instance with JWT interceptor in `frontend/src/api/client.js`
- [x] T012 Setup React AuthContext and AuthGuard routing in `frontend/src/context/AuthContext.jsx` and `frontend/src/App.jsx`
- [x] T012_T [P] Implement unit tests for bcrypt password hashing, JWT signature claims, and token expiration validation (SEC-002, SEC-003) in `backend/tests/unit/test_security.py`

---

## Phase 3: User Story 1 - HU-001: Registrar Empresa (Priority: P1)

**Goal**: Allow a business owner to register a new tenant and owner account.

**Independent Test**: Register a new company via `POST /api/v1/auth/register-company` and verify tenant creation, owner access, and input validation.

- [x] T013 [P] [US1] Create Tenant model in `backend/src/modules/auth/models.py`
- [x] T014 [P] [US1] Implement tenant & owner registration schemas in `backend/src/modules/auth/schemas.py`
- [x] T015 [US1] Implement company registration service & endpoint `POST /api/v1/auth/register-company` in `backend/src/modules/auth/router.py`
- [x] T016 [P] [US1] Build company registration view in `frontend/src/pages/RegisterCompany.jsx`
- [x] T017 [US1] Add unit test for company registration success (TC-001), duplicate tax_id/email rejection (TC-002), and input sanitization (SEC-001) in `backend/tests/unit/test_register_company.py`

---

## Phase 4: User Story 2 - HU-002: Iniciar Sesión (Priority: P1)

**Goal**: Allow registered users to authenticate securely and obtain JWT session token.

**Independent Test**: Login via `POST /api/v1/auth/login` with valid/invalid credentials and verify generic error responses and token claims.

- [x] T018 [P] [US2] Implement login request/response schemas in `backend/src/modules/auth/schemas.py`
- [x] T019 [US2] Implement login service & endpoint `POST /api/v1/auth/login` in `backend/src/modules/auth/router.py`
- [x] T020 [P] [US2] Build login view in `frontend/src/pages/Login.jsx`
- [x] T021 [US2] Add unit test for login authentication success (TC-003), invalid credentials generic 401 response (TC-004), and sensitive data protection (SEC-006) in `backend/tests/unit/test_auth.py`

---

## Phase 5: User Story 3 - HU-003: Gestionar Usuarios (Priority: P1)

**Goal**: Allow Admin users to create collaborators (`ADMIN` | `SELLER`) and toggle their status.

**Independent Test**: Create a user with role `SELLER` and verify they are blocked from user management (403 Forbidden).

- [x] T022 [P] [US3] Create User & Role models in `backend/src/modules/users/models.py`
- [x] T023 [P] [US3] Implement user schemas & RBAC validation in `backend/src/modules/users/schemas.py`
- [x] T024 [US3] Implement user management endpoints (`GET /api/v1/users`, `POST /api/v1/users`, `PATCH /api/v1/users/{id}/status`) in `backend/src/modules/users/router.py`
- [x] T025 [P] [US3] Build user management view for Admin in `frontend/src/pages/Users.jsx`
- [x] T026 [US3] Add unit test for user creation (TC-005), RBAC 403 Forbidden route protection on Seller (TC-006, SEC-004), and status toggle in `backend/tests/unit/test_rbac.py`

---

## Phase 6: User Story 4 - HU-004: Gestionar Productos (Priority: P1)

**Goal**: Allow authorized users to create, update, and soft-delete products.

**Independent Test**: Register a product with initial stock, update its price, and set status to INACTIVE.

- [x] T027 [P] [US4] Create Product model in `backend/src/modules/products/models.py`
- [x] T028 [P] [US4] Implement product schemas in `backend/src/modules/products/schemas.py`
- [x] T029 [US4] Implement product CRUD & soft-delete status endpoint in `backend/src/modules/products/router.py`
- [x] T030 [P] [US4] Build product management view in `frontend/src/pages/Products.jsx`
- [x] T031 [US4] Add unit test for product creation success (TC-007), input validation (SEC-001), and soft-delete inactivating products with transaction history (TC-008) in `backend/tests/unit/test_products.py`

---

## Phase 7: User Story 5 - HU-005: Gestionar Clientes (Priority: P1)

**Goal**: Allow authorized users to manage customer directory and auto-seed default "Consumidor Final".

**Independent Test**: Create a customer and verify default customer is available for sales.

- [x] T032 [P] [US5] Create Customer model in `backend/src/modules/customers/models.py`
- [x] T033 [P] [US5] Implement customer schemas in `backend/src/modules/customers/schemas.py`
- [x] T034 [US5] Implement customer endpoints and default "Consumidor Final" auto-seeding in `backend/src/modules/customers/router.py`
- [x] T035 [P] [US5] Build customer directory view in `frontend/src/pages/Customers.jsx`
- [x] T036 [US5] Add unit test for customer creation, default customer retrieval (TC-009), and soft-delete in `backend/tests/unit/test_customers.py`

---

## Phase 8: User Story 8 - HU-008: Registrar Compra (Priority: P2)

**Goal**: Allow authorized users to register merchandise purchases and increase product stock.

**Independent Test**: Register a purchase and verify product stock increases by the purchased quantity.

- [x] T037 [P] [US8] Create Purchase & PurchaseItem models in `backend/src/modules/purchases/models.py`
- [x] T038 [P] [US8] Implement purchase schemas in `backend/src/modules/purchases/schemas.py`
- [x] T039 [US8] Implement purchase registration endpoint `POST /api/v1/purchases` with atomic stock increment in `backend/src/modules/purchases/router.py`
- [x] T040 [P] [US8] Build stock purchase entry form in `frontend/src/pages/Purchases.jsx`
- [x] T041 [US8] Add unit test for purchase registration success (TC-010), atomic stock addition, and input validation in `backend/tests/unit/test_purchases.py`

---

## Phase 9: User Story 6 - HU-006: Registrar Venta (Priority: P1)

**Goal**: Allow authorized users to register sales with atomic stock deduction, row locking, and movement audit.

**Independent Test**: Register a sale, verify exact decimal calculation, stock deduction, and rejection when stock is insufficient.

- [x] T042 [P] [US6] Create Sale, SaleItem & InventoryMovement models in `backend/src/modules/sales/models.py`
- [x] T043 [P] [US6] Implement sale schemas with decimal math validation in `backend/src/modules/sales/schemas.py`
- [x] T044 [US6] Implement sale registration endpoint `POST /api/v1/sales` with pessimistic row lock (`FOR UPDATE`), atomic stock deduction & movement logging in `backend/src/modules/sales/router.py`
- [x] T045 [P] [US6] Build sales terminal / POS view in `frontend/src/pages/Sales.jsx`
- [x] T046 [US6] Add unit test for atomic sale transaction success (TC-011), row locking concurrency resolution (TC-013, SEC-007), and negative stock rejection (TC-012, QA-003) in `backend/tests/unit/test_sales.py`

---

## Phase 10: User Story 7 - HU-007: Consultar Ventas (Priority: P2)

**Goal**: Allow authorized users to view sales history and detailed receipts.

**Independent Test**: Fetch sales history list and verify receipt line items, totals, and confirmed immutability match.

- [x] T047 [P] [US7] Implement sales query & detail endpoints `GET /api/v1/sales` in `backend/src/modules/sales/router.py`
- [x] T048 [P] [US7] Build sales history view in `frontend/src/pages/SalesHistory.jsx`
- [x] T049 [US7] Add integration test for sales history querying (TC-014) and confirmed sales immutability verification (QA-004) in `backend/tests/integration/test_sales_history.py`

---

## Phase 11: User Story 9 - HU-009: Consultar Inventario (Priority: P1)

**Goal**: Allow authorized users to consult current stock levels derived from sales and purchases.

**Independent Test**: Consult inventory and verify stock values match net sales and purchases.

- [x] T050 [P] [US9] Implement inventory query endpoint `GET /api/v1/products` with stock filter in `backend/src/modules/products/router.py`
- [x] T051 [P] [US9] Build inventory consultation view in `frontend/src/pages/InventoryView.jsx`
- [x] T052 [US9] Add unit test for inventory stock calculation derived from sales and purchases (TC-015) in `backend/tests/unit/test_inventory.py`

---

## Phase 12: User Story 10 - HU-010: Consultar Resumen del Negocio (Priority: P2)

**Goal**: Allow Admin users to view executive metrics (total sales, counts) isolated by tenant.

**Independent Test**: Access summary endpoint as Admin and verify metrics match exact tenant aggregations.

- [x] T053 [P] [US10] Implement executive metrics calculation endpoint `GET /api/v1/dashboard/summary` in `backend/src/modules/dashboard/router.py`
- [x] T054 [P] [US10] Build executive dashboard view in `frontend/src/pages/Dashboard.jsx`
- [x] T055 [US10] Add integration test for executive metrics aggregation (TC-016) & Admin-only RBAC protection (SEC-004) in `backend/tests/integration/test_dashboard.py`

---

## Phase 13: Polish, Security Hardening & QA Gate Verification

**Purpose**: Multi-tenant security hardening, migrations, and end-to-end QA Gate validation.

- [x] T056 [P] Implement multi-tenant isolation integration test suite verifying 0 data leakage between Tenants (TC-017, SEC-005, QA-002) in `backend/tests/integration/test_tenant_isolation.py`
- [x] T057 [P] Execute database migration scripts via Alembic in `backend/alembic/versions/`
- [x] T058 Execute quickstart validation guide scenarios per `quickstart.md` and verify >=80% test coverage gate (QA-001, QA-005, QA-006)
- [x] T059 [P] Update documentation, API contract references, and test traceability matrix in `docs/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - starts immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish & QA Gate (Phase 13)**: Depends on all user stories being complete

### User Story Sequence

- **Step 1 (Foundation & Auth)**: US1 (HU-001) → US2 (HU-002)
- **Step 2 (RBAC & Catalogs)**: US3 (HU-003) → US4 (HU-004) → US5 (HU-005)
- **Step 3 (Core Transactions)**: US8 (HU-008 Compra) → US6 (HU-006 Venta)
- **Step 4 (Queries & Dashboard)**: US9 (HU-009 Inventario) → US7 (HU-007 Consultar Ventas) → US10 (HU-010 Resumen Negocio)

---

## Parallel Execution Opportunities

- All Setup tasks marked `[P]` (T003, T004, T005_T) can run in parallel.
- All Foundational tasks marked `[P]` (T006, T007, T008, T010, T011, T012_T) can run in parallel.
- Once Foundational phase completes, frontend UI views `[P]`, backend models `[P]`, and testing tasks `[P]` for different user stories can be worked on in parallel by team members.

---

## Testing Strategy & QA Gates

1. **Automated Testing Command**:
   - Backend: `pytest backend/tests -v`
   - Frontend: `npm --prefix frontend test`
2. **QA Gate Verification**:
   - Pass 100% of multi-tenant isolation tests (`TC-017`, `SEC-005`, `QA-002`).
   - Pass 100% of atomic sale stock deduction & concurrency tests (`TC-011`, `TC-012`, `TC-013`, `SEC-007`, `QA-003`).
   - Pass 100% of RBAC permission route tests (`TC-006`, `TC-016`, `SEC-004`).
