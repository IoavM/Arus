# Quickstart Validation Guide: Demo Day Enhancements

**Feature**: `002-demo-day-enhancements`
**Date**: 2026-08-21
**Spec**: [spec.md](spec.md) · **Contracts**: [contracts/endpoints.md](contracts/endpoints.md)

Guía de validación manual por HU, independiente entre sí — cada sección puede ejecutarse sola, sin requerir que las otras tres HU estén implementadas. Reutiliza el mismo entorno del baseline (`docker compose up --build`, ver `README.md`).

---

## Prerrequisitos comunes

1. Sistema levantado vía `docker compose up --build` (o entorno local equivalente al del baseline).
2. Una empresa y usuario Administrador ya registrados (`POST /api/v1/auth/register-company`), o reutilizar uno existente.
3. Backend tests: `pytest backend/tests -v` — cada HU agrega su propio archivo de test (`test_min_stock.py`, `test_sales_filter.py`, `test_categories.py`, `test_change_password.py`) que debe pasar en verde de forma aislada.

---

## HU-011: Stock mínimo

1. Crear un producto con `current_stock=5`, `min_stock=10`.
2. `GET /api/v1/products` → verificar que el producto trae `"min_stock": 10` y que en la UI (`/products`) aparece marcado como "Stock bajo" (porque `5 < 10`).
3. Editar el producto subiendo `current_stock` a `15` (vía `PUT /api/v1/products/{id}`, sin tocar `min_stock`).
4. Consultar de nuevo → la marca "Stock bajo" ya no debe aparecer.
5. Registrar una venta de ese producto (`POST /api/v1/sales`) → debe completarse con normalidad, sin ningún bloqueo relacionado a `min_stock`.
6. Verificar negativamente: no debe llegar ningún correo, notificación ni existir ningún proceso en background asociado — no hay nada que verificar porque no se implementa (confirmación de exclusión).

---

## HU-012: Filtro de historial de ventas

1. Registrar al menos 2 ventas a clientes distintos, en momentos distintos.
2. `GET /api/v1/sales` (sin filtros) → debe listar todas, orden más reciente primero (comportamiento actual sin cambios).
3. `GET /api/v1/sales?customer_id={id_cliente_A}` → solo ventas de ese cliente.
4. `GET /api/v1/sales?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD` → solo ventas dentro del rango.
5. Combinar ambos parámetros → intersección correcta.
6. `GET /api/v1/sales?customer_id={uuid-de-otro-tenant-o-inexistente}` → debe devolver `[]`, no error.
7. En la UI (`/sales-history`), aplicar los mismos filtros desde los controles nuevos y verificar visualmente el mismo resultado.

---

## HU-013: Categorías de producto

1. `POST /api/v1/categories` con `{"name": "Bebidas"}` → 201.
2. `POST /api/v1/categories` de nuevo con el mismo nombre → 400 (duplicado en el tenant).
3. `GET /api/v1/categories` → lista incluye "Bebidas".
4. Crear o editar un producto asignando `category_id` de "Bebidas" → `GET /api/v1/products` refleja la categoría.
5. Crear un producto sin `category_id` → sigue funcionando con total normalidad en venta/compra/inventario (verificar que `category_id` es `null` en la respuesta y no genera error).
6. Intentar asociar un producto a un `category_id` inexistente o de otro tenant → 400.
7. En la UI (`/products`), verificar que el selector de categoría y la columna/badge de categoría se muestran correctamente.

---

## HU-014: Cambio de contraseña propia

1. Autenticarse (`POST /api/v1/auth/login`) con un usuario existente → obtener token.
2. `POST /api/v1/auth/change-password` con `current_password` incorrecta → 400, mensaje genérico.
3. `POST /api/v1/auth/change-password` con `current_password` correcta y `new_password` válida (≥6 caracteres) → 200.
4. `POST /api/v1/auth/login` con la contraseña **anterior** → debe fallar (401).
5. `POST /api/v1/auth/login` con la contraseña **nueva** → debe funcionar (200), mismo `role_id` y `tenant_id` que antes.
6. Verificar en la UI: nueva ruta `/change-password` accesible desde el Sidebar para ambos roles (`Administrador` y `Vendedor`), sin afectar `/users` ni el flujo de `/login`.

---

## Validación cruzada post-integración (solo cuando 2+ HU ya estén en `main`)

- Si HU-011 y HU-013 están ambas integradas: ejecutar `alembic heads` en `backend/` y confirmar que devuelve **un único head** (ver `plan.md §6` — si devuelve dos, falta el paso manual de reconciliación de `down_revision`).
- Ejecutar la suite completa `pytest backend/tests -v` una vez más tras cualquier integración, para confirmar que ninguna HU rompió a otra.
