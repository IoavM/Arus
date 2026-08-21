# Phase 0 Research: Technical Decisions for Arus ERP Baseline

**Feature**: `001-initial-baseline`  
**Date**: 2026-08-20  
**Spec**: [spec.md](file:///c:/Users/ioavm/OneDrive/Escritorio/IOAV/Arus/specs/001-initial-baseline/spec.md)  
**Constitution**: [constitution.md](file:///c:/Users/ioavm/OneDrive/Escritorio/IOAV/Arus/.specify/memory/constitution.md)

---

## Technical Decisions Summary

### 1. Backend Python Framework: FastAPI
* **Decision**: Select **FastAPI** (Python 3.11+) as the backend web framework.
* **Rationale**:
  * Out-of-the-box support for async operation, high performance, and automatic OpenAPI schema generation.
  * Native integration with Pydantic for strict request/response data validation and sanitization.
  * Modular router structure (`APIRouter`) allowing a clean **Monolito Modular** organization by domain (auth, users, products, customers, sales, purchases, inventory, dashboard).
* **Alternatives Considered**:
  * *Django / Django REST Framework*: Heavy ORM/admin overhead, less flexible for custom multi-tenant middleware and explicit API contracts.
  * *Flask*: Requires assembling multiple third-party libraries for validation, async DB, and OpenAPI schemas.

### 2. Frontend Framework & State Management: React (Vite + Context API / Axios)
* **Decision**: **Vite + React (JavaScript/TypeScript)** with standard React Context for Auth/Tenant state and Vanilla CSS for styling.
* **Rationale**:
  * Lightweight, fast build times, and zero unnecessary abstraction overhead.
  * Clean component structure for pages (`/login`, `/dashboard`, `/products`, `/customers`, `/sales`, `/purchases`, `/users`).
  * Axios instance configured with request interceptors for automatic session/token attachment and centralized HTTP error handling.
* **Alternatives Considered**:
  * *Redux / Zustand*: Overkill for the initial 10 HUs baseline; React Context + local state is cleaner and faster to implement in 2 days.

### 3. Database & Access Strategy: PostgreSQL + SQLAlchemy 2.0 (Async) + Alembic
* **Decision**: **PostgreSQL** using **SQLAlchemy 2.0 Async Session** and **Alembic** for schema migrations.
* **Rationale**:
  * Guarantees strict transactional integrity (ACID) for Sales and Purchases.
  * Supports `DECIMAL(12, 2)` for exact monetary calculations avoiding floating-point rounding errors.
  * Enables clean multi-tenant filtering in SQLAlchemy query mixins and database session events.
* **Alternatives Considered**:
  * *Raw SQL (psycopg2)*: High risk of SQL injection and tedious manual mapping.
  * *Peewee / TortoiseORM*: Less mature ecosystem and migration tooling compared to SQLAlchemy + Alembic.

### 4. Multi-Tenant Isolation Strategy: Logical Multi-Tenancy (Foreign Key `tenant_id` + Backend Middleware)
* **Decision**: **Shared Database, Shared Schema with Mandatory `tenant_id` Column** on all tenant-bound tables, enforced by backend middleware and query scope.
* **Rationale**:
  * Simplest and most reliable deployment for a 2-day implementation window while maintaining 100% isolation.
  * Backend dependency injection in FastAPI automatically extracts `tenant_id` from the authenticated session/token and injects it into all database queries.
  * Completely prevents cross-tenant data leakage.
* **Alternatives Considered**:
  * *Schema per Tenant*: Complex migration execution and dynamic connection pooling overhead unsuited for tight deadlines.

### 5. Authentication & Authorization (RBAC): JWT HttpOnly Cookie / Bearer Token + Custom FastAPI Guards
* **Decision**: **JWT Token** containing `user_id`, `tenant_id`, and `role` (`Administrador` | `Vendedor`), validated by FastAPI dependency guards (`require_role(["Administrador"])`).
* **Rationale**:
  * Statelesness for backend API calls with explicit tenant context in token payload.
  * Backend enforcement guarantees that `Vendedor` receives `403 Forbidden` if attempting to call `/api/v1/users` or `/api/v1/dashboard/summary`.
* **Alternatives Considered**:
  * *Server-side sessions in Redis*: Adds extra infrastructure dependency.

### 6. Testing Strategy: pytest (Backend) + Vitest / Testing Library (Frontend)
* **Decision**: **pytest** with `pytest-asyncio` for unit/API integration tests; **Vitest** for frontend component validation.
* **Rationale**:
  * Rapid execution of API contract tests and transactional unit tests (e.g. verifying stock deduction on sale and stock rebound on failure).
