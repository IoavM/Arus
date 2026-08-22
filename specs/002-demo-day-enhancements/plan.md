# Implementation Plan: Demo Day Enhancements

**Branch**: `002-demo-day-enhancements` | **Date**: 2026-08-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-demo-day-enhancements/spec.md`

**Objetivo de este plan**: preparar la implementación **paralela** de HU-011 a HU-014 para el Demo Day, donde el profesor asigna una HU al azar a cada uno de 4 integrantes. El análisis siguiente está basado en la lectura directa del código real del repositorio (no en arquitectura asumida) — todos los archivos, campos y patrones citados fueron verificados en `backend/` y `frontend/` antes de escribir este documento.

---

## Summary

Cuatro incrementos aditivos sobre la línea base ya desplegada (001-initial-baseline): (1) filtro de historial de ventas por cliente/fecha, (2) indicador de stock mínimo, (3) categorías de producto, y (4) cambio de contraseña propia. El enfoque técnico reutiliza exactamente el stack, los patrones de dependencia FastAPI (`get_current_user`, `get_current_tenant_id`) y las convenciones de modelo/schema/router ya existentes en `backend/src/modules/*`. La prioridad de diseño de este plan es **minimizar el acoplamiento entre las cuatro HU a nivel de archivo**, dado que se implementarán en cuatro ramas distintas por cuatro personas distintas simultáneamente.

---

## Technical Context

**Language/Version**: Python 3.11+ (backend), JavaScript / React 18 (frontend) — idéntico al baseline, no se introduce ningún lenguaje ni versión nueva.

**Primary Dependencies**:
- Backend (ya declaradas en `backend/pyproject.toml`, reutilizadas sin cambios): `fastapi>=0.110`, `pydantic>=2.6`, `sqlalchemy>=2.0.28` (async), `asyncpg>=0.29`, `alembic>=1.13`, `pyjwt>=2.8`, `passlib[bcrypt]>=1.7.4`.
- Frontend (ya declaradas en `frontend/package.json`, reutilizadas sin cambios): `react@18.2`, `react-router-dom@6.22`, `axios@1.6`, `vite@5.1`.
- **No se agrega ninguna dependencia nueva** en ninguna de las cuatro HU.

**Storage**: PostgreSQL en producción (vía `asyncpg`, ver `backend/src/database.py`). Los tests backend usan **SQLite en memoria** (`sqlite+aiosqlite:///:memory:`, ver `backend/tests/conftest.py`) con tablas creadas directamente desde los modelos SQLAlchemy (`Base.metadata.create_all`) — **sin pasar por Alembic**. Este es un hecho verificado del código real con una consecuencia importante para la estrategia de migraciones (ver §6).

**Testing**: `pytest` + `pytest-asyncio` + `httpx.AsyncClient` (patrón idéntico al usado en los 4 archivos de test ya existentes). **No hay suite de frontend configurada**: `Vitest` se menciona en `specs/001-initial-baseline/plan.md` pero no está en `frontend/package.json` ni existen archivos de test bajo `frontend/`; es una aspiración del baseline no materializada. Esta feature **no introduce Vitest ni ninguna herramienta de test de frontend nueva** (violaría "no introduzcas tecnologías nuevas"); la validación de UI de las 4 HU queda manual, vía `quickstart.md`, igual que el resto del sistema hoy.

**Target Platform**: contenedor Docker (backend `uvicorn` + frontend `nginx`, ver `docker-compose.yml`), navegadores modernos — sin cambios.

**Project Type**: Monolito Modular Web (`backend/` + `frontend/`) — las 4 HU se insertan dentro de la estructura de módulos ya existente, sin alterar la arquitectura.

**Performance Goals / Constraints**: se heredan sin cambios los del baseline (API < 200ms p95, aislamiento multi-tenant 100%). Ninguna de las 4 HU introduce operaciones pesadas, colas ni procesos en segundo plano (explícitamente prohibido para HU-011 por el spec).

**Scale/Scope**: 4 incrementos aditivos; 1 tabla nueva (`categories`), 1 tabla existente extendida de forma aditiva (`products` +2 columnas nullable/con default), 0 tablas modificadas de forma incompatible, 0 tablas eliminadas.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Evaluación |
|---|---|
| **I. Priorización del Usuario** | PASS. Las 4 HU son mejoras de usabilidad/operatividad sin comprometer seguridad ni integridad de datos. |
| **III. Monolito Modular** | PASS. HU-013 se implementa como módulo nuevo autocontenido (`backend/src/modules/categories/`), replicando el patrón ya usado por `customers/`, `products/`, etc. Ninguna HU introduce microservicios ni acoplamiento nuevo entre módulos existentes. |
| **IV. Seguridad by Design** | PASS. HU-014 reutiliza `get_password_hash`/`verify_password` (`backend/src/security.py`) sin introducir un mecanismo nuevo; ninguna HU expone secretos al frontend. |
| **V. Multi-tenancy Nativo** | PASS. `categories` incluye `tenant_id` obligatorio siguiendo el mismo patrón que `products`/`customers`; el filtro de ventas (HU-012) y `min_stock` (HU-011) operan siempre dentro del `tenant_id` ya resuelto por `get_current_tenant_id`. |
| **VI. Autorización Declarativa** | PASS. Las 4 HU reutilizan `get_current_user`/`require_role` de `backend/src/shared/dependencies.py` **sin modificar ese archivo** — se agregan endpoints protegidos con las dependencias ya existentes, cumpliendo literalmente "el sistema DEBE permitir la adición de nuevos roles y permisos sin requerir reestructuraciones". |
| **VII. Integridad Transaccional** | PASS. Ninguna HU toca la lógica transaccional de `sales/router.py` o `purchases/router.py` (el `FOR UPDATE` y el cálculo de totales quedan intactos); HU-012 es de solo lectura. |
| **VIII. Auditoría Inmutable** | PASS (no aplica). HU-011/012/013/014 no son escrituras financieras/contables/de inventario (no generan `inventory_movements`), por lo que no requieren el registro de auditoría del Principio VIII — documentado explícitamente en `spec.md §0.1`. |
| **IX. Calidad Automatizada** | PASS. Cada HU incluye al menos un test backend (`pytest`) derivado de sus Acceptance Scenarios, siguiendo el patrón real de `backend/tests/unit/*.py`. |
| **X. SDD como Control** | PASS. Este plan deriva estrictamente de `spec.md` (HU-011 a HU-014); no se agrega ninguna capacidad no especificada. |
| **XI. Anti-sobreingeniería (YAGNI)** | PASS. Categoría se modela como FK simple 1-a-muchos (no many-to-many) porque el spec no pide múltiples categorías por producto — ver `research.md` para el razonamiento explícito. |
| **XII. Desarrollo Enfilado / Git / Trabajo Paralelo** | **GATE PRINCIPAL DE ESTE PLAN.** El principio exige explícitamente que "los módulos centrales DEBEN minimizarse en puntos de fricción para evitar conflictos de integración". Este plan dedica las secciones §5–§8 exclusivamente a este gate. Ver hallazgo de conflicto real (HU-011 × HU-013) y su mitigación. |
| **XIII. DevOps Reproducible** | PASS. No se modifica `docker-compose.yml` ni la separación de configuración por entorno. |

**Resultado del Gate**: PASA, con una advertencia documentada y mitigada (no un incumplimiento): HU-011 y HU-013 comparten 4 archivos por diseño de dominio (ambas extienden `Product`), tratado en detalle en §6–§7 con una estrategia concreta de minimización, tal como exige el Principio XII.

---

## Project Structure

### Documentation (this feature)

```text
specs/002-demo-day-enhancements/
├── spec.md              # Ya generado (/speckit-specify)
├── plan.md              # Este archivo (/speckit-plan)
├── research.md          # Phase 0 (decisiones de diseño, sin tecnologías nuevas)
├── data-model.md        # Phase 1 (columnas/tablas nuevas, delta sobre 001)
├── contracts/
│   └── endpoints.md     # Phase 1 (contrato de los 4 endpoints nuevos/extendidos)
├── quickstart.md         # Phase 1 (guía de validación manual por HU)
└── tasks.md              # Phase 2 — NO se crea en este comando (/speckit-tasks)
```

### Source Code — archivos reales afectados por HU

```text
backend/
├── alembic/versions/
│   ├── 21b58fdf539e_initial_baseline.py   # existente, NO se modifica
│   ├── <nueva>_add_min_stock_to_products.py    # HU-011 (nueva)
│   └── <nueva>_add_categories.py               # HU-013 (nueva)
├── src/
│   ├── main.py                            # HU-013 modifica (2 líneas: import + include_router)
│   ├── modules/
│   │   ├── products/
│   │   │   ├── models.py                  # HU-011 modifica (+min_stock) · HU-013 modifica (+category_id)
│   │   │   ├── schemas.py                 # HU-011 modifica · HU-013 modifica
│   │   │   └── router.py                  # HU-011 modifica (2 líneas) · HU-013 modifica (2 líneas)
│   │   ├── categories/                    # HU-013 — módulo nuevo completo
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── router.py
│   │   ├── sales/
│   │   │   └── router.py                  # HU-012 modifica (solo este archivo en backend)
│   │   ├── auth/
│   │   │   ├── schemas.py                 # HU-014 modifica
│   │   │   └── router.py                  # HU-014 modifica
│   │   └── users/                         # HU-014 NO toca este módulo (ver §8)
│   └── shared/dependencies.py             # NINGUNA HU lo modifica (se reutiliza tal cual)
└── tests/
    ├── conftest.py                        # NINGUNA HU lo modifica (fixtures ya suficientes)
    ├── unit/test_min_stock.py             # HU-011 (nuevo)
    ├── unit/test_categories.py            # HU-013 (nuevo)
    ├── unit/test_change_password.py       # HU-014 (nuevo)
    └── integration/test_sales_filter.py   # HU-012 (nuevo)

frontend/src/
├── App.jsx                                # HU-014 modifica (+1 ruta) — ninguna otra HU lo toca
├── components/Sidebar.jsx                 # HU-014 modifica (+1 link) — ninguna otra HU lo toca
├── pages/
│   ├── Products.jsx                       # HU-011 modifica · HU-013 modifica
│   ├── SalesHistory.jsx                   # HU-012 modifica (único archivo frontend de HU-012)
│   ├── Users.jsx                          # NINGUNA HU lo toca
│   └── ChangePassword.jsx                 # HU-014 — archivo nuevo
```

**Structure Decision**: se mantiene el Monolito Modular ya existente. HU-013 introduce un módulo nuevo (`categories/`) siguiendo el mismo patrón de `customers/`; las demás HU no crean módulos backend nuevos.

---

## Análisis de Aislamiento por HU (resumen ejecutivo)

| HU | Archivos backend tocados | Archivos frontend tocados | ¿Toca `main.py`, `App.jsx` o `Sidebar.jsx`? | Migración nueva |
|---|---|---|---|---|
| **HU-011** (stock mínimo) | `products/models.py`, `products/schemas.py`, `products/router.py` | `Products.jsx` | No | Sí |
| **HU-012** (filtro ventas) | `sales/router.py` **(único)** | `SalesHistory.jsx` **(único)** | No | No |
| **HU-013** (categorías) | `categories/*` (nuevo), `products/models.py`, `products/schemas.py`, `products/router.py` | `Products.jsx` | Sí, `main.py` (+2 líneas) | Sí |
| **HU-014** (contraseña) | `auth/schemas.py`, `auth/router.py` | `ChangePassword.jsx` (nuevo) | Sí, `App.jsx` + `Sidebar.jsx` (+1 línea c/u) | No |

**Conclusión directa de la tabla**:
- **HU-012 queda aislada exclusivamente en ventas/historial**, tal como pediste: un solo archivo backend, un solo archivo frontend, cero contacto con `main.py`/`App.jsx`/`Sidebar.jsx`/migraciones. Es la HU con menor riesgo de conflicto de todo el conjunto.
- **HU-014 queda aislada exclusivamente en autenticación**: no toca `backend/src/modules/users/` ni `frontend/src/pages/Users.jsx` en absoluto (el endpoint de autoservicio se ubica en `auth/router.py`, no en `users/router.py` — ver justificación en `research.md`). Es la única HU que toca `App.jsx`/`Sidebar.jsx`, y como ninguna otra HU los toca, **no hay conflicto cruzado posible** en esos dos archivos.
- **HU-011 y HU-013 son las únicas dos con solapamiento real de archivos** — ambas extienden la entidad `Product`. Esto es estructural (ambas HU agregan un atributo opcional a `products`) y no se puede eliminar sin cambiar el alcance de las historias, lo cual el usuario indicó explícitamente que NO se debe hacer. Se minimiza en las secciones §6–§7.

---

## §6. Estrategia de Migraciones (HU-011 y HU-013)

**Hallazgo clave verificado en el código**: hoy existe una única migración (`21b58fdf539e_initial_baseline.py`, `down_revision = None`) — es decir, un único "head" de Alembic. Además, **el suite de tests no depende de Alembic en absoluto** (`conftest.py` crea las tablas con `Base.metadata.create_all` directamente desde los modelos SQLAlchemy). Esto tiene una consecuencia favorable importante: **HU-011 y HU-013 pueden desarrollarse, testearse y demostrarse cada una en su propia rama de forma 100% independiente**, sin que ninguna bloquee a la otra — el conflicto de Alembic es un problema exclusivamente de **integración a `main`**, no de desarrollo ni de pruebas.

**Estrategia**:
1. Cada rama crea su propia migración con `down_revision = '21b58fdf539e'` (el head actual), de forma independiente. Nombres sugeridos: `add_min_stock_to_products` (HU-011) y `add_categories` (HU-013).
2. Ninguna de las dos modifica la migración `21b58fdf539e` existente ni la migración de la otra HU.
3. **En integración final** (no antes, no es tarea de `/speckit-implement` por HU individual): quien integre la **segunda** de las dos ramas a `main` DEBE, como último paso, actualizar el `down_revision` de su migración para que apunte a la revisión de la que ya se integró primero (o ejecutar `alembic merge heads` si ambas ya fueron mezcladas generando dos heads). Este paso es manual y depende del orden real de integración, que no puede conocerse de antemano — se documenta como intervención humana requerida (ver tasks.md, que se generará en el siguiente comando).
4. Ambas migraciones son **puramente aditivas** (`ADD COLUMN ... NULL` o `... DEFAULT`), por lo que no hay riesgo de pérdida de datos ni de bloqueo de tabla prolongado en PostgreSQL, sin importar el orden en que finalmente se apliquen.

---

## §7. Estrategia de Separación de Responsabilidades (HU-011 vs HU-013 en `products/*`)

Dado que ambas HU necesariamente tocan `products/models.py`, `products/schemas.py`, `products/router.py` y `Products.jsx`, la estrategia no es evitar el contacto (imposible sin cambiar el alcance) sino **reducir la probabilidad de colisión línea-a-línea** y **contener el 90% de la lógica nueva fuera de esos archivos compartidos**:

1. **Separación de responsabilidades real**: toda la lógica propia de categorías (crear, listar, validar nombre único por tenant) vive **exclusivamente** en el módulo nuevo `backend/src/modules/categories/` — HU-013 solo toca `products/*` para exponer un campo `category_id` opcional (lectura/escritura), nunca para la lógica de negocio de categorías en sí. HU-011 no tiene ningún módulo propio: toda su lógica (el campo `min_stock` y el cálculo "stock bajo") vive dentro de `products/*` y `Products.jsx`.
2. **Puntos de anclaje explícitos y no adyacentes** para minimizar colisión de líneas en el merge de Git:
   - `products/models.py`: HU-011 agrega la columna `min_stock` inmediatamente después de `current_stock`; HU-013 agrega `category_id` inmediatamente después de `status` (antes de `created_at`) — son líneas distintas y no contiguas.
   - `products/schemas.py`: HU-011 agrega `min_stock` al final de cada clase (`ProductCreateRequest`, `ProductUpdateRequest`, `ProductResponse`); HU-013 agrega `category_id` también al final de cada clase, **después** del campo de HU-011 por convención (quien integre segundo simplemente añade su línea al final, sin tocar la de la otra HU).
   - `products/router.py`: cada una agrega **una sola línea** dentro de `create_product`/`update_product` (`min_stock=payload.min_stock` / `category_id=payload.category_id`) — son asignaciones independientes dentro del mismo bloque `Product(...)`, que Git fusiona automáticamente en la gran mayoría de los casos al no ser la misma línea.
   - `Products.jsx`: HU-011 agrega su campo de formulario justo después del campo "Stock Inicial" ya existente; HU-013 agrega su selector justo después del campo "Descripción" — bloques JSX en zonas distintas del mismo formulario. Este es el único punto donde un conflicto de merge (no funcional, solo textual) es razonablemente probable y se resuelve manualmente en minutos (dos `<div className="form-group">` adyacentes, nunca lógica contradictoria).
3. **Reducción de cambios en archivos globales**: `main.py` lo toca únicamente HU-013 (registro del router de categorías); HU-011 no lo toca en absoluto. Es el mínimo footprint posible dado que categorías es, por diseño, un recurso HTTP nuevo.
4. **Tareas independientes**: en `tasks.md` (siguiente comando), la tarea que edita el archivo compartido será la **última** tarea de cada HU en cada archivo — permitiendo que cada persona desarrolle y valide el resto de su historia (modelo/schema propio, endpoint propio, test) antes de tocar el archivo compartido.
5. **Integración final**: recomendación operativa (no técnica) — si ambas HU-011 y HU-013 son asignadas en la misma ronda del Demo Day, se sugiere que quien integre segundo haga `git pull`/rebase sobre `main` justo antes de tocar `products/*`, revise el diff de esos 3 archivos con `git diff`, y ejecute la suite completa de `pytest` una vez más tras el rebase. Ninguna acción de este paso requiere coordinación *durante* el desarrollo — solo en el momento de integrar a `main`.

---

## §8. Confirmación de Aislamiento de HU-012 y HU-014

Verificado explícitamente contra el código real:

- **HU-012**: no requiere cambios en `sales/models.py` ni `sales/schemas.py` — los filtros (`customer_id`, `date_from`, `date_to`) se implementan como parámetros `Query(...)` opcionales directamente en la firma de `list_sales()` dentro de `sales/router.py`, sin necesidad de un nuevo schema Pydantic. Es el único archivo backend que toca. No se acerca a `products/*`, `users/*`, `auth/*`, `main.py`, `App.jsx` ni `Sidebar.jsx`.
- **HU-014**: se implementa como `POST /api/v1/auth/change-password` dentro de `auth/router.py` (reutilizando `get_current_user` para resolver la identidad desde el JWT, nunca desde un parámetro de la solicitud). **No toca `backend/src/modules/users/`** (ni `models.py`, ni `schemas.py`, ni `router.py`) — ese módulo queda completamente intacto, a pesar de ser uno de los hotspots señalados a vigilar. Tampoco toca `frontend/src/pages/Users.jsx`.

---

## §9. Estrategia de Implementación Paralela e Integración

1. **Branching**: cada integrante crea su rama desde el estado actual de `main` (`feature/hu-011-stock-minimo`, `feature/hu-012-filtro-ventas`, `feature/hu-013-categorias`, `feature/hu-014-cambio-password`), consistente con el Principio XII de la Constitución.
2. **Orden de integración**: no importa el orden salvo para el par HU-011/HU-013 (ver §6, paso de `down_revision`). HU-012 y HU-014 pueden integrarse en cualquier momento, antes, entre o después de las otras dos, sin ningún ajuste adicional.
3. **Validación pre-integración por HU**: cada rama corre `pytest backend/tests -v` de forma aislada (verde sin depender de las otras 3 ramas) y valida su(s) escenario(s) de `quickstart.md` correspondiente(s).
4. **Validación post-integración** (una vez las 4 estén en `main`): re-ejecutar la suite completa de `pytest`, y si HU-011 y HU-013 llegaron ambas, verificar que solo existe un head de Alembic (`alembic heads` debe listar exactamente uno).

---

## Constitution Check — Re-evaluación Post-Diseño (tras Phase 1)

Tras generar `research.md`, `data-model.md`, `contracts/endpoints.md` y `quickstart.md`, se repite el gate: ninguna decisión de diseño de Phase 1 introduce una violación nueva.
- `data-model.md` confirma que ambas columnas nuevas de `products` son aditivas (nullable/default) y que `categories` sigue el mismo patrón `tenant_id` obligatorio que el resto de tablas del baseline (Principio V).
- `contracts/endpoints.md` confirma que los 4 endpoints nuevos/extendidos reutilizan `get_current_user`/`get_current_tenant_id` sin excepción y sin necesidad de tocar `shared/dependencies.py` (Principio VI).
- No se generó ningún `openapi.json` estático nuevo (decisión documentada en `contracts/endpoints.md`) — no aplica al Principio X ya que la trazabilidad HU → FR → endpoint queda cubierta por `spec.md` + este contrato.

**Resultado**: GATE PASA sin cambios respecto a la evaluación pre-diseño.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Ninguna | N/A | El único punto de fricción real (HU-011 × HU-013 en `products/*`) no es una violación de un principio constitucional — es una consecuencia estructural de que ambas HU extienden la misma entidad de negocio, exigida explícitamente por el enunciado de ambas historias (que el usuario indicó no modificar). Se mitiga operativamente en §6–§7, no requiere excepción a la Constitución. |
