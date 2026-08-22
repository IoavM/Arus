# Phase 1 API Contracts: Demo Day Enhancements

**Feature**: `002-demo-day-enhancements`
**Date**: 2026-08-21
**Spec**: [spec.md](spec.md)

Este documento describe los contratos de los endpoints nuevos/extendidos, en el mismo formato de referencia rápida usado por el resto del proyecto (los contratos canónicos y siempre actualizados quedan expuestos en tiempo real por FastAPI en `/api/v1/docs`, tal como ya ocurre para las HU del baseline — por eso no se genera un `openapi.json` estático nuevo, que quedaría desactualizado frente al autogenerado).

Todos los endpoints requieren `Authorization: Bearer <JWT>` salvo que se indique lo contrario, y todos resuelven el `tenant_id` desde el token (nunca desde el request), reutilizando `get_current_user` / `get_current_tenant_id` de `backend/src/shared/dependencies.py`.

---

## HU-011 — Stock mínimo (extiende endpoints existentes de `products`)

### `POST /api/v1/products` (extendido)
- **Request body** (agrega campo opcional): `{ ..., "min_stock": integer >= 0 (default 0) }`
- **Response 201**: `ProductResponse` ahora incluye `"min_stock": integer`.

### `PUT /api/v1/products/{product_id}` (extendido)
- **Request body** (agrega campo): `{ ..., "min_stock": integer >= 0 }`
- **Response 200**: `ProductResponse` incluye `"min_stock"`.

### `GET /api/v1/products` (sin cambios de firma)
- **Response 200**: cada item de `ProductResponse` incluye `"min_stock": integer`. El indicador "Stock bajo" se calcula en el frontend (`current_stock < min_stock`), no es un campo de la respuesta.

---

## HU-012 — Filtro de historial de ventas (extiende `GET /api/v1/sales`)

### `GET /api/v1/sales?customer_id={uuid}&date_from={date}&date_to={date}` (extendido)
- **Query params (todos opcionales, combinables)**:
  - `customer_id: UUID` — filtra por cliente.
  - `date_from: date` (`YYYY-MM-DD`) — límite inferior inclusive sobre `created_at`.
  - `date_to: date` (`YYYY-MM-DD`) — límite superior inclusive sobre `created_at`.
- **Response 200**: idéntica forma que hoy (`List[SaleResponse]`), ordenada por `created_at DESC`, ahora filtrada según los parámetros presentes.
- **Compatibilidad**: sin parámetros, respuesta idéntica a la actual.
- **Errores**: nunca retorna 404/400 por un `customer_id` inexistente o de otro tenant — retorna `[]` (evita revelar existencia de datos ajenos, ver spec Edge Cases).

---

## HU-013 — Categorías de producto (módulo nuevo `categories`)

### `POST /api/v1/categories`
- **Request body**: `{ "name": string (1-100 chars) }`
- **Response 201**: `{ "id": uuid, "tenant_id": uuid, "name": string, "created_at": datetime }`
- **Response 400**: nombre duplicado dentro del mismo tenant.

### `GET /api/v1/categories`
- **Response 200**: `List[CategoryResponse]` — solo categorías del tenant activo.

### `POST /api/v1/products` / `PUT /api/v1/products/{product_id}` (extendidos)
- **Request body** (agrega campo opcional): `{ ..., "category_id": uuid | null }`
- **Response 400**: si `category_id` no existe o pertenece a otro tenant.
- **Response 201/200**: `ProductResponse` incluye `"category_id": uuid | null`.

### `GET /api/v1/products` (sin cambios de firma)
- **Response 200**: cada item incluye `"category_id": uuid | null`.

---

## HU-014 — Cambio de contraseña propia (módulo `auth`)

### `POST /api/v1/auth/change-password`
- **Auth**: requerida (cualquier rol, `Administrador` o `Vendedor`) — identidad resuelta vía `get_current_user`, nunca vía parámetro de la solicitud.
- **Request body**: `{ "current_password": string, "new_password": string (min_length=6, misma regla que `RegisterCompanyRequest`/`UserCreateRequest`) }`
- **Response 200**: `{ "message": "Contraseña actualizada correctamente" }`
- **Response 400**: `current_password` incorrecta (mensaje genérico, sin revelar detalles).
- **Response 401**: sin sesión autenticada.
- **Efecto**: reemplaza `password_hash` del usuario autenticado usando `get_password_hash` (`backend/src/security.py`), sin alterar `role_id`, `status`, ni ningún otro campo.
