# Tasks: Demo Day Enhancements

**Input**: Design documents from `/specs/002-demo-day-enhancements/` (`plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/endpoints.md`, `quickstart.md`)

**Prerequisites**: `plan.md` ✅, `spec.md` ✅, `research.md` ✅, `data-model.md` ✅, `contracts/endpoints.md` ✅

**Mapeo de etiquetas**: esta feature usa `[HU-011]`/`[HU-012]`/`[HU-013]`/`[HU-014]` como etiqueta de historia (en vez de `[US#]` genérico), correspondiendo a `spec.md` así: HU-011 = User Story 2, HU-012 = User Story 1, HU-013 = User Story 3, HU-014 = User Story 4. Las cuatro comparten prioridad P1 (ver `spec.md`) — el orden de las fases abajo sigue el orden numérico de HU, no una jerarquía de valor.

**Independencia**: las cuatro HU parten del mismo estado actual de `main` (línea base 001 ya desplegada). Ninguna fase depende de que otra esté completa. Cada persona puede ejecutar `/speckit-implement` sobre su HU asignada sin esperar a las demás.

---

## Phase 1: Setup (Shared Infrastructure)

**No aplica.** La infraestructura compartida (app FastAPI, motor de base de datos async, middleware de tenant, autenticación JWT, guards RBAC) ya existe y está operativa en la línea base `001-initial-baseline`. Ninguna de las 4 HU requiere inicialización de proyecto, dependencias nuevas, ni configuración adicional — todas reutilizan `backend/pyproject.toml` / `frontend/package.json` tal cual están hoy. **0 tareas en esta fase.**

## Phase 2: Foundational (Blocking Prerequisites)

**No aplica.** No existe ningún prerrequisito bloqueante nuevo: `backend/src/shared/dependencies.py`, `backend/src/shared/models.py` y `backend/src/security.py` ya proveen todo lo necesario (`get_current_user`, `get_current_tenant_id`, `require_role`, `TenantMixin`, hashing de contraseñas) y **ninguna de las 4 HU los modifica** (verificado contra `plan.md`; no se encontró evidencia de que sea necesario). **0 tareas en esta fase.**

**Checkpoint**: las 4 fases de HU siguientes pueden comenzar de inmediato, en paralelo, cada una en su propia rama.

---

## Phase 3: HU-011 — Indicador de stock mínimo (Priority: P1)

**Goal**: permitir definir `min_stock` por producto y mostrar "Stock bajo" cuando `current_stock < min_stock`, sin ningún automatismo (FR-004, FR-005, FR-006 de `spec.md`).

**Independent Test**: crear un producto con `current_stock=5, min_stock=10` → debe listarse como "Stock bajo"; subir `current_stock` a 15 → la marca desaparece; registrar una venta sobre ese producto → se completa sin ningún bloqueo relacionado a `min_stock` (ver `quickstart.md`).

**Archivos que esta fase NO toca** (confirmado): `backend/src/shared/*`, `backend/src/security.py`, `backend/src/modules/users/*`, `backend/src/modules/sales/*`, `backend/src/modules/auth/*`, `backend/src/main.py`, `frontend/src/App.jsx`, `frontend/src/components/Sidebar.jsx`.

- [X] T001 [HU-011] Crear migración Alembic (`alembic revision -m "add_min_stock_to_products"`, con `down_revision = '21b58fdf539e'`, archivo nuevo en `backend/alembic/versions/`) que agregue `min_stock INTEGER NOT NULL DEFAULT 0 CHECK (min_stock >= 0)` a la tabla `products`; y agregar la columna equivalente `min_stock = Column(Integer, nullable=False, default=0)` en `backend/src/modules/products/models.py`, inmediatamente después de `current_stock` (no reordenar ni tocar ninguna otra columna existente). **No modificar** `backend/alembic/versions/21b58fdf539e_initial_baseline.py`.

- [X] T002 [HU-011] En `backend/src/modules/products/schemas.py`: agregar `min_stock: int = Field(0, ge=0)` al final de `ProductCreateRequest`, `min_stock: int = Field(..., ge=0)` al final de `ProductUpdateRequest`, y `min_stock: int` al final de `ProductResponse`. En `backend/src/modules/products/router.py`: en `create_product()` pasar `min_stock=payload.min_stock` al construir `Product(...)`, y en `update_product()` agregar la línea `product.min_stock = payload.min_stock`. No modificar la lógica de `toggle_product_status()` ni `list_products()` (el campo se expone automáticamente vía `ProductResponse`). *(Depende de T001 — requiere que la columna exista en el modelo.)*

- [X] T003 [P] [HU-011] En `frontend/src/pages/Products.jsx`: agregar un campo "Stock Mínimo" (`<input type="number" min="0">`) en el formulario de creación/edición, ubicado inmediatamente después del campo "Stock Inicial" existente (líneas ~198-210), incluyéndolo en `formData` (estado inicial, reset al abrir "Nuevo Producto", población en `handleEdit`, y el payload de `handleSave`); y agregar un badge visual "⚠ Stock bajo" en la tabla de productos cuando `p.current_stock < p.min_stock`, junto al badge de stock ya existente (línea ~124-128). El contrato de datos (`min_stock` en request/response) ya está fijado en `contracts/endpoints.md` — el código de UI puede escribirse sin esperar a T002, aunque la validación end-to-end sí lo requiere.

- [X] T004 [HU-011] Crear `backend/tests/unit/test_min_stock.py` (patrón `httpx.AsyncClient` + fixture `client` de `backend/tests/conftest.py`, igual que `test_sales.py`) cubriendo: (1) crear producto sin especificar `min_stock` → persiste `0` por defecto; (2) crear producto con `min_stock=10` y consultarlo → el valor persiste correctamente; (3) actualizar `min_stock` vía `PUT /api/v1/products/{id}` → refleja el nuevo valor; (4) un producto con `current_stock < min_stock` es identificable en la respuesta de `GET /api/v1/products` (los datos para que el frontend calcule "Stock bajo" están presentes y correctos); (5) enviar `min_stock=-1` → rechazado con HTTP 422 (validación `ge=0`, mismo patrón que `sale_price`). *(Depende de T001, T002.)*

**Checkpoint**: HU-011 completa y demostrable de forma aislada.

---

## Phase 4: HU-012 — Filtrar historial de ventas (Priority: P1)

**Goal**: filtrar `GET /api/v1/sales` por `customer_id` y/o rango de fechas, preservando aislamiento por tenant y el orden descendente ya existente (FR-001, FR-002, FR-003 de `spec.md`).

**Independent Test**: con ventas de 2+ clientes en fechas distintas, filtrar por cliente → solo sus ventas; filtrar por rango de fechas → solo las del rango; combinar ambos → intersección correcta; sin filtros → comportamiento idéntico al actual (ver `quickstart.md`).

**Archivos que esta fase NO toca** (confirmado): `backend/src/modules/products/*`, `backend/src/modules/sales/models.py`, `backend/src/modules/sales/schemas.py`, `backend/src/modules/auth/*`, `backend/src/modules/users/*`, `backend/src/main.py`, `backend/alembic/versions/`, `frontend/src/App.jsx`, `frontend/src/components/Sidebar.jsx`.

- [X] T005 [HU-012] En `backend/src/modules/sales/router.py`, extender la firma de `list_sales()` agregando tres parámetros opcionales: `customer_id: Optional[uuid.UUID] = Query(None)`, `date_from: Optional[date] = Query(None)`, `date_to: Optional[date] = Query(None)` (importar `date` de `datetime` y `Optional` ya está importado). No modificar aún el cuerpo de la función en esta tarea.

- [X] T006 [HU-012] En el cuerpo de `list_sales()` (mismo archivo, mismo endpoint), aplicar condicionalmente al `stmt` ya existente: `.where(Sale.customer_id == customer_id)` si `customer_id` fue provisto, `.where(Sale.created_at >= date_from)` si `date_from` fue provisto, `.where(Sale.created_at <= date_to + timedelta(days=1))` si `date_to` fue provisto (para incluir todo el día final, dado que `created_at` es `TIMESTAMPTZ`); mantener sin cambios el `.where(Sale.tenant_id == tenant_id)` y el `.order_by(Sale.created_at.desc())` ya existentes. Un `customer_id` de otro tenant o inexistente debe producir lista vacía (nunca error), porque el filtro por `tenant_id` ya lo excluye de forma natural. *(Depende de T005 — mismo archivo y función.)*

- [X] T007 [P] [HU-012] En `frontend/src/pages/SalesHistory.jsx`: agregar controles de filtro (un `<select>` de cliente poblado desde `GET /api/v1/customers`, y dos `<input type="date">` para `date_from`/`date_to`) antes de la tabla de ventas existente (línea ~34), un botón "Limpiar filtros", y un mensaje de estado vacío ("No hay ventas para el filtro aplicado"); llamar a `apiClient.get('/sales', { params: { customer_id, date_from, date_to } })` solo incluyendo los parámetros con valor. El contrato de query params ya está fijado en `contracts/endpoints.md` — el código de UI puede escribirse sin esperar a T006, aunque la validación end-to-end sí lo requiere.

- [X] T008 [HU-012] Crear `backend/tests/integration/test_sales_filter.py` (mismo patrón que `test_tenant_isolation.py`) cubriendo: (1) filtro por `customer_id` retorna solo ventas de ese cliente; (2) filtro por `date_from`/`date_to` retorna solo ventas dentro del rango; (3) combinación de ambos filtros retorna la intersección correcta; (4) sin filtros, comportamiento idéntico al actual (todas las ventas del tenant, orden descendente); (5) aislamiento multi-tenant: un `customer_id` perteneciente a otro tenant (creado con un segundo `register-company`) retorna lista vacía, nunca datos ni error. *(Depende de T006.)*

**Checkpoint**: HU-012 completa y demostrable de forma aislada — es la HU con menor superficie de archivos de las cuatro.

---

## Phase 5: HU-013 — Categorías de productos (Priority: P1)

**Goal**: crear/listar categorías y asociarlas opcionalmente a un producto, sin alterar reglas de venta, compra ni stock (FR-007, FR-008, FR-009 de `spec.md`).

**Independent Test**: crear categoría "Bebidas"; asociarla a un producto; consultarlo y verificar la asociación; verificar que un producto sin categoría sigue operando con normalidad (ver `quickstart.md`).

**Restricción de diseño (obligatoria)**: toda la lógica específica de categorías (creación, listado, validación de nombre único por tenant) vive exclusivamente en el módulo nuevo `backend/src/modules/categories/`. Los cambios en `backend/src/modules/products/*` se limitan **estrictamente** a exponer/persistir el campo `category_id` — ninguna tarea de esta fase debe refactorizar `Products.jsx` completo, ni mover código existente, ni tocar la lógica de `min_stock` (propiedad exclusiva de HU-011).

**Archivos que esta fase NO toca** (confirmado): `backend/src/modules/sales/*`, `backend/src/modules/auth/*`, `backend/src/modules/users/*`, `backend/src/shared/*`, `frontend/src/App.jsx`, `frontend/src/components/Sidebar.jsx`. **Archivo compartido con HU-011** (ver nota de concurrencia al final de este documento): `backend/src/modules/products/models.py`, `products/schemas.py`, `products/router.py`, `frontend/src/pages/Products.jsx`.

- [X] T009 [HU-013] Crear el módulo nuevo `backend/src/modules/categories/models.py` con el modelo `Category` (`id` UUID PK, `tenant_id` UUID FK a `tenants.id` ondelete RESTRICT indexado, `name` VARCHAR(100) NOT NULL, `created_at` TIMESTAMPTZ, `UniqueConstraint('tenant_id', 'name')`) — ver `data-model.md §2`. Crear migración Alembic (`alembic revision -m "add_categories"`, `down_revision = '21b58fdf539e'`, archivo nuevo en `backend/alembic/versions/`) que cree la tabla `categories` y agregue la columna `category_id UUID NULL` con FK a `categories.id` en la tabla `products`. En `backend/src/modules/products/models.py`, agregar **únicamente** `category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)` inmediatamente después de `status` (antes de `created_at`) — no tocar ninguna otra línea del archivo. **No modificar** `backend/alembic/versions/21b58fdf539e_initial_baseline.py` ni la columna `min_stock` de HU-011 si ya existe en la rama.

- [X] T010 [HU-013] Crear `backend/src/modules/categories/schemas.py` (`CategoryCreateRequest{name: str, min_length=1, max_length=100}`, `CategoryResponse{id, tenant_id, name, created_at}`) y `backend/src/modules/categories/router.py` con `POST /categories` (rechaza nombre duplicado en el tenant con HTTP 400) y `GET /categories` (lista solo las del tenant activo, vía `get_current_tenant_id`/`get_current_user`). Registrar el router en `backend/src/main.py` (agregar `from src.modules.categories.router import router as categories_router` e `app.include_router(categories_router, prefix=settings.API_V1_STR)`, sin tocar ninguna otra línea del archivo). En `backend/src/modules/products/schemas.py`, agregar **únicamente** `category_id: Optional[uuid.UUID] = None` al final de `ProductCreateRequest`, `ProductUpdateRequest` y `ProductResponse`. En `backend/src/modules/products/router.py`, agregar **únicamente** una línea en `create_product()` (`category_id=payload.category_id`) y una línea en `update_product()` (`product.category_id = payload.category_id`), validando antes que, si `category_id` fue provisto, exista y pertenezca al mismo `tenant_id` (HTTP 400 en caso contrario, mismo patrón que la validación de `customer_id` en `sales/router.py`). *(Depende de T009.)*

- [X] T011 [P] [HU-013] En `frontend/src/pages/Products.jsx`: agregar un selector de categoría (`<select>` poblado desde `GET /api/v1/categories`, con opción "Sin categoría") junto con un control simple para crear una categoría nueva inline (`POST /api/v1/categories`), ubicados inmediatamente después del campo "Descripción" existente (línea ~177-185) — bloque distinto y no adyacente al campo de HU-011 (que va después de "Stock Inicial"); incluir `category_id` en `formData` (mismos 4 puntos que T003 de HU-011: estado inicial, reset, `handleEdit`, payload de `handleSave`) y mostrar el nombre de categoría (o "Sin categoría") como columna/badge en la tabla. El contrato ya está fijado en `contracts/endpoints.md` — el código de UI puede escribirse sin esperar a T010, aunque la validación end-to-end sí lo requiere.

- [X] T012 [HU-013] Crear `backend/tests/unit/test_categories.py` cubriendo: (1) crear categoría → persiste correctamente; (2) listar categorías → retorna solo las del tenant activo; (3) asociar un producto a una categoría existente del mismo tenant → la asociación se refleja en `GET /api/v1/products`; (4) un producto sin `category_id` sigue operando con normalidad en creación/edición (no se rompe ni requiere el campo); (5) crear una categoría con nombre duplicado en el mismo tenant → HTTP 400; (6) aislamiento multi-tenant: intentar asociar un producto a una categoría de otro tenant (creado con un segundo `register-company`) → HTTP 400, y el listado de categorías de un tenant nunca incluye las de otro. *(Depende de T009, T010.)*

**Checkpoint**: HU-013 completa y demostrable de forma aislada.

---

## Phase 6: HU-014 — Cambio de contraseña propia (Priority: P1)

**Goal**: permitir a cualquier usuario autenticado cambiar su propia contraseña, validando la actual y reutilizando el hashing existente (FR-010, FR-011, FR-012 de `spec.md`).

**Independent Test**: login → cambiar contraseña con la actual correcta → logout → login con la nueva (funciona) → login con la anterior (rechazado) (ver `quickstart.md`).

**Archivos que esta fase NO toca** (confirmado — verificado explícitamente, no se encontró evidencia de necesidad real de tocarlos): `backend/src/modules/users/models.py`, `backend/src/modules/users/schemas.py`, `backend/src/modules/users/router.py`, `frontend/src/pages/Users.jsx`, `backend/src/shared/dependencies.py`, `backend/src/security.py` (se **reutiliza** `verify_password`/`get_password_hash` ya existentes, sin modificarlos), `backend/src/modules/products/*`, `backend/src/modules/sales/*`, `backend/alembic/versions/`.

- [ ] T013 [HU-014] En `backend/src/modules/auth/schemas.py`, agregar `ChangePasswordRequest{current_password: str, new_password: str = Field(..., min_length=6)}` (misma regla mínima que `RegisterCompanyRequest.password` y `UserCreateRequest.password`).

- [ ] T014 [HU-014] En `backend/src/modules/auth/router.py`, agregar `POST /change-password` (bajo el `router` ya existente con `prefix="/auth"`, quedando `POST /api/v1/auth/change-password`), protegido con `current_user: User = Depends(get_current_user)` (importar de `src.shared.dependencies`, mismo patrón usado en `products/router.py`). Lógica: verificar `verify_password(payload.current_password, current_user.password_hash)`; si falla, HTTP 400 con mensaje genérico ("Contraseña actual incorrecta") sin revelar más detalle; si es correcta, `current_user.password_hash = get_password_hash(payload.new_password)`, `db.commit()`, retornar `{"message": "Contraseña actualizada correctamente"}` con HTTP 200. No modificar `register_company()` ni `login()` en este archivo. *(Depende de T013.)*

- [ ] T015 [P] [HU-014] Crear `frontend/src/pages/ChangePassword.jsx` (mismo estilo que `Login.jsx`/`RegisterCompany.jsx`: formulario con "Contraseña actual", "Nueva contraseña", "Confirmar nueva contraseña" con validación de coincidencia en cliente antes de enviar, y manejo de error igual al patrón `err.response?.data?.detail` ya usado en el resto del frontend). En `frontend/src/App.jsx`, agregar la ruta `<Route path="/change-password" element={<ProtectedRoute><ChangePassword /></ProtectedRoute>} />` (sin `requiredRole`, accesible para `Administrador` y `Vendedor`) junto a las demás rutas protegidas. En `frontend/src/components/Sidebar.jsx`, agregar un `<NavLink to="/change-password">` visible para ambos roles (fuera de los bloques `{isAdmin && (...)}`), ubicado junto al bloque de usuario/logout al final del sidebar. El contrato ya está fijado en `contracts/endpoints.md` — el código de UI puede escribirse sin esperar a T014, aunque la validación end-to-end sí lo requiere.

- [ ] T016 [HU-014] Crear `backend/tests/unit/test_change_password.py` cubriendo: (1) `current_password` incorrecta → HTTP 400, la contraseña no cambia; (2) cambio exitoso con `current_password` correcta y `new_password` válida → HTTP 200; (3) tras el cambio, `POST /api/v1/auth/login` con la nueva contraseña → HTTP 200, mismo `role_id`/`tenant_id` que antes; (4) tras el cambio, login con la contraseña anterior → HTTP 401; (5) `POST /api/v1/auth/change-password` sin header `Authorization` → HTTP 401. *(Depende de T014.)*

**Checkpoint**: HU-014 completa y demostrable de forma aislada — junto con HU-012, es de las de menor superficie de archivos.

---

## Dependencies & Execution Order

### Entre fases (HU)

**Ninguna fase depende de otra.** Las 4 fases (Phase 3 a Phase 6) pueden iniciarse simultáneamente por 4 personas distintas, cada una en su propia rama, partiendo del mismo commit de `main`. No existe ninguna tarea que diga "esperar a HU-XXX".

### Dentro de cada fase (intra-HU)

| HU | Cadena de dependencia |
|---|---|
| HU-011 | T001 → T002 → {T003, T004} (T003 y T004 pueden iniciarse tan pronto el contrato esté fijado; su *validación end-to-end* requiere T002) |
| HU-012 | T005 → T006 → {T007, T008} |
| HU-013 | T009 → T010 → {T011, T012} |
| HU-014 | T013 → T014 → {T015, T016} |

### Parallel Opportunities

- **Entre HU** (el caso central del Demo Day): T001, T005, T009, T013 pueden ejecutarse simultáneamente por 4 personas distintas — con una única salvedad de coordinación (no de dependencia): T001 (HU-011) y T009 (HU-013) escriben ambas en `backend/src/modules/products/models.py` y crean cada una su propia migración desde el mismo head de Alembic. Esto **no bloquea** a ninguna de las dos (cada rama compila y prueba de forma aislada, ver `plan.md §6`); solo requiere el paso de reconciliación humana descrito abajo al integrar ambas a `main`.
- **Dentro de cada HU**: las tareas de UI (`T003`, `T007`, `T011`, `T015`, todas marcadas `[P]`) pueden escribirse en paralelo con la tarea de backend correspondiente de su misma HU, porque el contrato de datos ya está fijado en `contracts/endpoints.md` — solo la *validación funcional end-to-end* requiere que la tarea de backend esté terminada.

---

## Nota Especial de Concurrencia: HU-011 × HU-013 (archivos compartidos)

Documentado y esperado (ver `plan.md §7`) — **no se cambiaron las historias para eliminarlo**, se minimizó su impacto:

| Archivo compartido | Qué agrega HU-011 | Qué agrega HU-013 |
|---|---|---|
| `backend/src/modules/products/models.py` | `min_stock` (después de `current_stock`) | `category_id` (después de `status`) |
| `backend/src/modules/products/schemas.py` | `min_stock` al final de cada clase | `category_id` al final de cada clase |
| `backend/src/modules/products/router.py` | 1 línea en `create_product()` + 1 en `update_product()` | 1 línea en `create_product()` + 1 en `update_product()` |
| `frontend/src/pages/Products.jsx` | Campo tras "Stock Inicial" + badge en tabla | Selector tras "Descripción" + columna en tabla |

**Ninguna de las dos tareas depende de la otra** — ambas pueden implementarse y probarse (`pytest`) de forma 100% aislada en su propia rama. El único paso que requiere intervención humana ocurre **al integrar ambas ramas a `main`**, no antes: quien integre la segunda de las dos debe (a) hacer rebase sobre `main`, (b) actualizar el `down_revision` de su migración para que apunte a la revisión de la que ya se integró primero (o ejecutar `alembic merge heads` si ya generaron dos heads), y (c) re-correr `pytest backend/tests -v` una vez más. Esto queda fuera del alcance de `/speckit-implement` por HU individual — es un paso de integración, no una tarea de historia.

---

## Implementation Strategy

Cada persona ejecuta `/speckit-implement` sobre su HU asignada (Phase 3, 4, 5 o 6) desde el estado actual de `main`, en su propia rama (`feature/hu-011-...`, `feature/hu-012-...`, `feature/hu-013-...`, `feature/hu-014-...`). Dentro de cada HU, el orden de las 4 tareas ya refleja la dependencia real (persistencia/modelo → schema/endpoint → {UI, tests}). Al finalizar su HU, cada persona corre `pytest backend/tests -v` de forma aislada (debe pasar en verde sin necesitar las otras 3 ramas) y valida su sección correspondiente de `quickstart.md` antes de solicitar integración a `main`.
