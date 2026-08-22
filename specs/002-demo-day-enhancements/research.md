# Phase 0 Research: Demo Day Enhancements

**Feature**: `002-demo-day-enhancements`
**Date**: 2026-08-21
**Spec**: [spec.md](spec.md)

---

Esta feature no introduce ninguna tecnología, lenguaje ni dependencia nueva — el `Technical Context` de `plan.md` no contiene ningún `NEEDS CLARIFICATION`. Por eso este documento no investiga alternativas de stack, sino que registra las **decisiones de diseño** necesarias para resolver ambigüedades de implementación dentro del stack ya existente, priorizando siempre minimizar el acoplamiento entre las cuatro HU (ver `plan.md §5-§8`).

---

## Decisión 1: Dos migraciones Alembic independientes, no una combinada

- **Decision**: HU-011 y HU-013 crean cada una su propia migración, ambas con `down_revision = '21b58fdf539e'` (el head actual).
- **Rationale**: permite que ambas ramas se desarrollen y testeen en paralelo sin que ninguna espere a que la otra termine. El suite de tests no depende de Alembic (usa `Base.metadata.create_all` sobre SQLite en memoria — ver `backend/tests/conftest.py`), así que esta independencia no tiene costo en cobertura de pruebas.
- **Alternatives considered**: una única migración combinada que agregue `min_stock` y `category_id` a la vez — rechazada porque forzaría a que una de las dos HU dependiera de que la otra estuviera implementada primero, violando el requisito explícito de independencia total entre las cuatro historias.

## Decisión 2: `category_id` como FK simple 1-a-muchos, no muchos-a-muchos

- **Decision**: `products.category_id` es una columna `UUID` nullable con FK a `categories.id` (un producto tiene cero o una categoría).
- **Rationale**: el spec ("clasificar los productos mediante categorías") no exige múltiples categorías por producto. El propio baseline ya usa este patrón (p. ej. `users.role_id` es un FK simple, no una tabla de asociación) — mantenerlo consistente respeta el Principio XI (anti-sobreingeniería / YAGNI) y minimiza el número de tablas nuevas a una sola (`categories`), reduciendo también la superficie de la migración.
- **Alternatives considered**: tabla de asociación `product_categories` (muchos-a-muchos) — rechazada por complejidad no solicitada; además seguiría requiriendo tocar `products/router.py`/`schemas.py` para exponer la categoría en la respuesta del producto, así que no habría reducido el acoplamiento con HU-011.

## Decisión 3: Endpoint de cambio de contraseña vive en `auth/router.py`, no en `users/router.py`

- **Decision**: `POST /api/v1/auth/change-password`, implementado en el módulo `auth`, reutilizando `get_current_user` de `shared/dependencies.py` para resolver la identidad desde el JWT.
- **Rationale**: `users/router.py` hoy solo contiene endpoints protegidos con `require_role(["ADMIN"])` (gestión administrativa de colaboradores, HU-003). Un endpoint de autoservicio (accesible para cualquier rol autenticado, sobre su propia cuenta) es conceptualmente distinto y ponerlo en `users/router.py` aumentaría el riesgo de una regresión accidental en el guard de rol de ese archivo. Colocarlo en `auth/router.py` también logra el aislamiento total que pide el usuario ("HU-014 debe quedar aislada principalmente en autenticación/usuario"): cero contacto con `users/*` o `Users.jsx`.
- **Alternatives considered**: `PATCH /api/v1/users/me/password` en el módulo `users` — rechazada por acoplar HU-014 a un archivo (`users/router.py`) que ninguna otra parte de esta feature necesita tocar, sin ninguna ganancia funcional.

## Decisión 4: Filtro de ventas como query params opcionales sobre el endpoint existente, sin nuevo schema

- **Decision**: `customer_id`, `date_from`, `date_to` se agregan como parámetros `Query(None)` directamente en la firma de `list_sales()` (`sales/router.py`), sin crear un `SaleFilterRequest` en `sales/schemas.py`.
- **Rationale**: mismo patrón ya usado en `products/router.py` (`query`, `status_filter` como `Query(None)`) — consistencia con el código real existente. Evita tocar `sales/schemas.py`, reduciendo aún más la superficie de archivos de HU-012 (queda en un único archivo backend).
- **Alternatives considered**: nuevo endpoint `GET /api/v1/sales/search` — rechazado por duplicar innecesariamente el recurso; un schema `SaleFilterRequest` en el body — rechazado porque filtrar una colección vía `GET` con query params (no un body) es el patrón REST ya establecido en todo el proyecto.

## Decisión 5: Indicador "Stock bajo" calculado en el frontend, no en el backend

- **Decision**: `ProductResponse` solo expone el valor crudo `min_stock`; la comparación `current_stock < min_stock` para mostrar el badge "Stock bajo" ocurre en `Products.jsx`, igual que ya ocurre hoy con los umbrales de color del badge de stock (`current_stock > 10 ? 'success' : ...`).
- **Rationale**: cero lógica nueva en el backend más allá de persistir/exponer un entero; consistente con el patrón ya existente en el mismo archivo/línea de `Products.jsx`.
- **Alternatives considered**: campo booleano `is_low_stock` calculado en el backend — funcionalmente válido pero rechazado por ser superficie adicional innecesaria para un valor trivialmente derivable de dos enteros ya presentes en la respuesta.

## Decisión 6: Puntos de anclaje explícitos en archivos compartidos (HU-011 × HU-013)

- **Decision**: ver `plan.md §7` — cada HU tiene asignada una posición de línea distinta y no adyacente dentro de `products/models.py`, `products/schemas.py`, `products/router.py` y `Products.jsx`.
- **Rationale**: no elimina el contacto con archivos compartidos (estructuralmente inevitable, ambas HU extienden `Product`), pero reduce la probabilidad de un conflicto de merge línea-a-línea a prácticamente el mínimo posible sin cambiar el alcance de ninguna historia.
- **Alternatives considered**: forzar un orden fijo de implementación (p. ej. "HU-011 siempre primero") — rechazada porque contradice el requisito explícito de que las cuatro historias deben poder asignarse y comenzarse en cualquier orden, al azar.

---

**Output de esta fase**: todas las decisiones de diseño quedaron resueltas; no queda ningún `NEEDS CLARIFICATION` pendiente antes de Phase 1.
