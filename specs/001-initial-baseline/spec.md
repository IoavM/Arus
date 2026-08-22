# Feature Specification: Línea Base Inicial Arus ERP

**Feature Branch**: `001-initial-baseline`  
**Created**: 2026-08-20  
**Last Updated**: 2026-08-21  
**Status**: Draft (Clarified with Cybersecurity, Quality & Automated Testing Requirements)  
**Input**: User description: "Especificación inicial del producto Arus ERP basada en las 10 Historias de Usuario iniciales (HU-001 a HU-010) ampliada con requisitos de ciberseguridad, calidad y estrategia de pruebas automatizadas."

---

## Clarifications

### Session 2026-08-20

* **Q1: ¿Cómo se gestionan las compras en HU-008?** → **A**: La compra se registra seleccionando productos, cantidades adquiridas y precio/costo unitario. La entidad `Proveedor` queda fuera del MVP.
* **Q2: ¿Se permiten ajustes manuales de inventario en v1?** → **A**: No. Los ajustes manuales quedan fuera del MVP. El inventario en v1 se actualiza exclusivamente por movimientos de `VENTA` (egreso) y `COMPRA` (ingreso).
* **Q3: ¿Es posible modificar o anular una venta confirmada?** → **A**: No. Una venta confirmada es inmutable en v1 y no se puede editar. Las anulaciones, cancelaciones y devoluciones quedan fuera del MVP para proteger la trazabilidad.
* **Q4: ¿Cómo se maneja la eliminación de productos y clientes?** → **A**: Los productos y clientes con historial transaccional NO se eliminan físicamente; únicamente se inactivan (`estado: inactivo`) para ser ocultados en nuevas operaciones. El borrado físico solo se permite para registros sin ninguna dependencia transaccional.
* **Q5: ¿Cuáles son los roles de usuario predefinidos e iniciales?** → **A**: El sistema implementará inicialmente dos roles: `Administrador` (acceso completo a la empresa, usuarios y resumen) y `Vendedor` (operaciones comerciales, registro de ventas, consulta de clientes/productos/inventario; sin acceso a gestión de usuarios ni resumen del negocio). El modelo sigue siendo extensible para futuros roles.
* **Q6: ¿Cómo se define el criterio de éxito SC-005 para ser objetivamente verificable?** → **A**: Un usuario sin experiencia previa completa exitosamente el flujo básico secuencial de registrar un producto, registrar un cliente y realizar una venta durante una sesión de prueba guiada sin requerir asistencia técnica externa.

### Session 2026-08-21

* **Q7: ¿Qué alcance de Ciberseguridad, Calidad y Pruebas Automatizadas debe agregarse al Specify?** → **A**: Se especifican formalmente los requisitos de seguridad de datos, autenticación/autorización, aislamiento multi-tenant, manejo seguro de secretos, matriz de escenarios de prueba (casos exitosos y de error) para todas las 10 HUs y criterios de aceptación de calidad (QA Gate) sin alterar el alcance funcional original.

---

## 1. Objetivo y Alcance

### 1.1 Objetivo General
Desarrollar la primera línea base funcional de **Arus**, un ERP web multi-tenant diseñado para pequeñas y medianas empresas (PYMEs) y micronegocios, ofreciendo una experiencia de usuario clara, intuitiva y accesible sin sacrificar la seguridad ni la integridad de los datos.

### 1.2 Alcance de la Línea Base (10 HUs)
La línea base incluye 10 capacidades funcionales clave:
1. **HU-001**: Registrar empresa (*tenant* inicial y propietario).
2. **HU-002**: Iniciar sesión (autenticación segura y sesión de *tenant*).
3. **HU-003**: Gestionar usuarios (colaboradores bajo roles `Administrador` y `Vendedor`).
4. **HU-004**: Gestionar productos (catálogo, precios, existencias e inactivación lógica).
5. **HU-005**: Gestionar clientes (directorio de compradores e inactivación lógica).
6. **HU-006**: Registrar venta (transacción comercial inmutable con descuento automático de stock).
7. **HU-007**: Consultar ventas (historial y detalle de comprobantes).
8. **HU-008**: Registrar compra (ingreso de mercancía por productos, cantidades y costo unitario sin entidad proveedor).
9. **HU-009**: Consultar inventario (existencias actuales derivadas de ventas y compras).
10. **HU-010**: Consultar resumen del negocio (indicadores ejecutivos exclusivos para rol Administrador).

---

## 2. Fuera de Alcance del MVP

Las siguientes funcionalidades quedan **excluidas explícitamente** de la versión inicial para garantizar la entrega en plazo con alta calidad y bajo acoplamiento:
* **Modificación, anulación o devolución de ventas y compras**: Una transacción confirmada es inmutable.
* **Gestión de Proveedores**: Las compras registran productos, cantidades y costo sin catálogo de proveedores.
* **Ajustes manuales de inventario**: La UI y lógica de v1 solo procesa movimientos por VENTA y COMPRA.
* **Descuentos avanzados o promociones**: No se permiten reglas complejas de precios en v1.
* **Métodos de pago avanzados, pagos parciales o créditos**.
* **Facturación electrónica legal/fiscal integrada**.
* **Reportes avanzados, gráficos complejos o exportación de archivos (PDF/Excel)**.
* **Alertas automáticas por stock mínimo**.
* **Auditoría avanzada de lecturas**: Solo se auditan escrituras/transacciones de ventas, compras y usuarios.
* **Soporte Offline-First o PWA**.

---

## 3. Historias de Usuario (HU-001 a HU-010)

### User Story 1 - HU-001: Registrar empresa (Priority: P1)
**Como** propietario de un negocio  
**quiero** registrar mi empresa en Arus  
**para** configurar el espacio de trabajo aislado de mi negocio.

* **Valor**: Habilita la creación del *tenant* inicial.
* **Prueba independiente**: Registrar una empresa con datos válidos y verificar la creación del espacio de trabajo y el usuario administrador.
* **Escenarios de Aceptación**:
  1. *Registro exitoso*: Dados los datos válidos (nombre comercial, NIT/documento fiscal, correo y contraseña), al enviar el formulario se crea el *tenant* y el usuario propietario con rol `Administrador`.
  2. *Duplicados*: Dados datos con correo o documento fiscal ya registrado, el sistema bloquea el registro con un mensaje claro.
  3. *Validación*: Campos vacíos o con formato inválido son rechazados en el formulario.

### User Story 2 - HU-002: Iniciar sesión (Priority: P1)
**Como** usuario registrado  
**quiero** iniciar sesión en Arus  
**para** acceder de forma segura a la información de mi empresa.

* **Valor**: Seguridad y contexto de sesión por *tenant*.
* **Prueba independiente**: Acceder con credenciales válidas y verificar el establecimiento del contexto autenticado.
* **Escenarios de Aceptación**:
  1. *Autenticación exitosa*: Credenciales correctas inician sesión y redirigen al espacio de la empresa.
  2. *Credenciales inválidas*: Error genérico deniega el acceso sin revelar cuál dato falló.
  3. *Rutas protegidas*: Navegación sin sesión redirige obligatoriamente al login.

### User Story 3 - HU-003: Gestionar usuarios (Priority: P1)
**Como** administrador  
**quiero** gestionar los usuarios de mi empresa  
**para** controlar quién puede acceder al sistema asignando los roles `Administrador` o `Vendedor`.

* **Valor**: Administración de colaboradores bajo autorización RBAC.
* **Prueba independiente**: Crear un usuario con rol `Vendedor` e inactivarlo, verificando que los cambios de permiso apliquen de inmediato.
* **Escenarios de Aceptación**:
  1. *Crear usuario*: Administrador crea colaborador especificando si su rol es `Administrador` o `Vendedor`.
  2. *Inactivar usuario*: Usuario inactivado pierde de inmediato la capacidad de autenticarse o realizar solicitudes.
  3. *Restricción de acceso*: Los usuarios con rol `Vendedor` no pueden acceder a la gestión de usuarios.
  4. *Aislamiento*: La lista de usuarios muestra únicamente los colaboradores del *tenant* activo.

### User Story 4 - HU-004: Gestionar productos (Priority: P1)
**Como** usuario autorizado  
**quiero** gestionar los productos de mi empresa  
**para** mantener actualizada la información de los artículos comercializables.

* **Valor**: Base para el catálogo de venta y control de existencias.
* **Prueba independiente**: Registrar un producto con precio y stock inicial, actualizar sus datos e inactivarlo si posee historial.
* **Escenarios de Aceptación**:
  1. *Crear producto*: Registro con SKU, nombre, descripción, precio de venta y stock inicial mayor o igual a cero.
  2. *Editar producto*: Modificar precio o descripción sin alterar historial transaccional previo.
  3. *Inactivar producto*: Un producto con transacciones no se borra físicamente; pasa a estado `inactivo` para no ser seleccionado en nuevas ventas.
  4. *Borrado físico condicional*: Se permite borrado físico únicamente si el producto no posee ninguna transacción registrada.

### User Story 5 - HU-005: Gestionar clientes (Priority: P1)
**Como** usuario autorizado  
**quiero** gestionar los clientes de mi empresa  
**para** mantener organizada la información de compradores.

* **Valor**: Identificación de clientes en operaciones comerciales.
* **Prueba independiente**: Registrar cliente, consultar lista e inactivar cliente con ventas pasadas.
* **Escenarios de Aceptación**:
  1. *Crear cliente*: Registro con nombre/razón social, documento y datos de contacto.
  2. *Editar cliente*: Actualización de datos de contacto.
  3. *Inactivar cliente*: Si el cliente tiene ventas asociadas, se inactiva manteniendo intacto el historial.
  4. *Cliente por defecto*: Se incluye un cliente genérico ("Consumidor Final") para ventas rápidas de mostrador.

### User Story 6 - HU-006: Registrar venta (Priority: P1)
**Como** usuario autorizado (`Administrador` o `Vendedor`)  
**quiero** registrar una venta  
**para** controlar las operaciones comerciales y actualizar el inventario automáticamente.

* **Valor**: Operación central de ingresos y deducción de stock.
* **Prueba independiente**: Venta de artículos con stock disponible descuenta las existencias exactas.
* **Escenarios de Aceptación**:
  1. *Venta exitosa*: Registro atómico e inmutable calcula el total, descuenta el stock y guarda la auditoría.
  2. *Venta a Consumidor Final*: Permite registrar ventas seleccionando el cliente genérico por defecto o un cliente registrado.
  3. *Stock insuficiente*: Solicitud mayor a las existencias rebota la venta sin modificar inventario.
  4. *Inmutabilidad*: La venta confirmada queda guardada de forma permanente y no se puede editar ni borrar.

### User Story 7 - HU-007: Consultar ventas (Priority: P2)
**Como** usuario autorizado (`Administrador` o `Vendedor`)  
**quiero** consultar las ventas realizadas  
**para** revisar el historial comercial y comprobar transacciones.

* **Valor**: Visibilidad y transparencia operativa.
* **Prueba independiente**: Consultar el listado de ventas y verificar detalle de items y totales.
* **Escenarios de Aceptación**:
  1. *Listado ordenado*: Muestra ventas de la más reciente a la más antigua con cliente, fecha y total.
  2. *Detalle de venta*: Vista con renglones de artículos, precios unitarios y sub-totales.
  3. *Aislamiento*: Prohibida la consulta de ventas de otros *tenants*.

### User Story 8 - HU-008: Registrar compra (Priority: P2)
**Como** usuario autorizado  
**quiero** registrar una compra  
**para** abastecer el negocio e incrementar las existencias de productos.

* **Valor**: Abastecimiento de inventario sin complejidad de catálogo de proveedores.
* **Prueba independiente**: Registrar la compra de N productos especificando cantidades y costo unitario, verificando incremento en stock.
* **Escenarios de Aceptación**:
  1. *Compra exitosa*: Registro atómico especificando productos, cantidades y costo unitario incrementa el stock e inscribe el movimiento.
  2. *Sin proveedor obligatorio*: No se requiere seleccionar proveedor en v1.
  3. *Validación*: Cantidades menores o iguales a cero son rechazadas.

### User Story 9 - HU-009: Consultar inventario (Priority: P1)
**Como** usuario autorizado  
**quiero** consultar el inventario  
**para** conocer las existencias disponibles de mis productos.

* **Valor**: Control de disponibilidad de mercancía.
* **Prueba independiente**: Consultar stock y validar que coincida exactamente con las ventas y compras registradas.
* **Escenarios de Aceptación**:
  1. *Consulta de existencias*: Muestra SKU, nombre, precio y stock actual.
  2. *Filtro*: Búsqueda por código o nombre filtra artículos en tiempo real.
  3. *Origen de movimientos*: Existencias consolidadas únicamente por transacciones de `VENTA` y `COMPRA`.

### User Story 10 - HU-010: Consultar resumen del negocio (Priority: P2)
**Como** propietario o administrador (`Administrador`)  
**quiero** consultar un resumen de la actividad del negocio  
**para** obtener una visión general de la operación.

* **Valor**: Dashboard ejecutivo del negocio.
* **Prueba independiente**: Acceder como Administrador y verificar que los totales agregados reflejen la suma exacta de ventas y conteos del *tenant*.
* **Escenarios de Aceptación**:
  1. *Métricas clave*: Muestra total monetario vendido, número de ventas, productos activos y clientes registrados.
  2. *Acceso restringido*: Intento de acceso por un usuario con rol `Vendedor` es rechazado con error de permiso.

---

## 4. Requisitos Funcionales

* **FR-001**: El sistema DEBE permitir la creación de un nuevo *tenant* (empresa) registrando al usuario propietario con rol `Administrador`.
* **FR-002**: El sistema DEBE autenticar usuarios mediante credenciales seguras y fijar la sesión al contexto del *tenant*.
* **FR-003**: El sistema DEBE permitir a los administradores crear, editar rol (`Administrador` o `Vendedor`) e inactivar colaboradores de su empresa.
* **FR-004**: El sistema DEBE validar la autorización en backend según el modelo **Usuario → Tenant → Rol (`Administrador` | `Vendedor`) → Permisos**.
* **FR-005**: El sistema DEBE restringir el acceso a la gestión de usuarios (HU-003) y al resumen del negocio (HU-010) exclusivamente al rol `Administrador`.
* **FR-006**: El sistema DEBE permitir crear, consultar y editar productos (SKU, nombre, descripción, precio y stock inicial) e inactivar productos con historial.
* **FR-007**: El sistema DEBE permitir crear, consultar y editar clientes e inactivar clientes con historial transaccional.
* **FR-008**: El sistema DEBE proveer un cliente genérico por defecto ("Consumidor Final") para ventas rápidas de mostrador.
* **FR-009**: El sistema DEBE registrar ventas asociando cliente, renglones de productos y cantidades, calculando totales exactos.
* **FR-010**: El sistema DEBE registrar la venta y el descuento de inventario en una única transacción atómica e inmutable.
* **FR-011**: El sistema DEBE rechazar el registro de ventas cuando la cantidad solicitada sea mayor al stock disponible.
* **FR-012**: El sistema DEBE permitir consultar el historial e información detallada de ventas pasadas sin permitir su modificación ni anulación en v1.
* **FR-013**: El sistema DEBE registrar compras (especificando productos, cantidades y costo unitario sin entidad proveedor) e incrementar atómicamente el stock.
* **FR-014**: El sistema DEBE presentar la lista consolidada de inventario derivada únicamente de movimientos de `VENTA` y `COMPRA`.
* **FR-015**: El sistema DEBE consolidar las métricas clave de negocio (ventas totales, conteos) aisladas por *tenant* para el Administrador.
* **FR-016**: El sistema DEBE registrar auditoría inmutable de ventas, compras e ingresos/egresos de stock guardando usuario, timestamp y entidad afectada.
* **FR-017**: El sistema DEBE garantizar el aislamiento absoluto de consultas por *tenant* en la capa de persistencia.

---

## 5. Requisitos de Experiencia y Diseño (UX/UI)

* **Lenguaje de Negocio**: La interfaz DEBE usar términos comerciales sencillos ("Ventas", "Compras", "Productos", "Clientes", "Inventario") sin terminología técnica.
* **Diseño Adaptativo**: UI completamente funcional y legible en escritorios, tabletas y smartphones.
* **Prevención de Errores**: Formularios con validaciones en tiempo real antes del envío.
* **Eficiencia en Venta**: Selección rápida de productos y soporte para cliente por defecto ("Consumidor Final").

---

## 6. Navegación y Experiencia de Usuario

* **Rutas de Navegación**:
  * `/login` - Pantalla de inicio de sesión.
  * `/register-company` - Registro de nueva empresa y administrador.
  * `/dashboard` - Resumen del negocio (Solo `Administrador`).
  * `/products` - Gestión de productos e inventario (`Administrador` y `Vendedor`).
  * `/customers` - Gestión de clientes (`Administrador` y `Vendedor`).
  * `/sales` - Registro y consulta de ventas (`Administrador` y `Vendedor`).
  * `/purchases` - Registro de compras (`Administrador` y `Vendedor`).
  * `/users` - Gestión de usuarios colaboradores (Solo `Administrador`).

---

## 7. Entidades Principales y Modelo de Datos

* **Tenant**: ID, nombre comercial, NIT/ID fiscal, fecha creación.
* **Usuario**: ID, Tenant_ID, nombre, correo, contraseña (hash), Rol_ID (`Administrador` | `Vendedor`), estado (`activo` | `inactivo`).
* **Rol & Permiso**: ID, nombre (`Administrador`, `Vendedor`), lista de permisos.
* **Producto**: ID, Tenant_ID, SKU, nombre, descripción, precio_venta, stock_actual, estado (`activo` | `inactivo`).
* **Cliente**: ID, Tenant_ID, nombre, documento_id, teléfono, correo, estado (`activo` | `inactivo`).
* **Venta**: ID, Tenant_ID, Cliente_ID, Usuario_ID, fecha_hora (ISO 8601), monto_total, estado (`confirmada`). *Inmutable en v1*.
* **DetalleVenta**: ID_Venta, Producto_ID, cantidad, precio_unitario, subtotal.
* **Compra**: ID, Tenant_ID, Usuario_ID, fecha_hora (ISO 8601), monto_total.
* **DetalleCompra**: ID_Compra, Producto_ID, cantidad, precio_costo, subtotal.
* **MovimientoInventario**: ID, Tenant_ID, Producto_ID, tipo (`VENTA` | `COMPRA`), cantidad, stock_previo, stock_posterior, Usuario_ID, fecha_hora. *(El tipo `AJUSTE` queda reservado para iteraciones futuras, no se implementa en v1)*.

---

## 8. Reglas de Negocio y Métricas

* **Integridad Monetaria**: Todos los valores monetarios DEBEN manejarse con tipos de precisión exacta (evitando punto flotante).
* **Inmutabilidad de Ventas**: Una venta confirmada no se edita ni anula en v1.
* **Stock No Negativo**: Las ventas no pueden dejar el stock menor a 0.
* **Aislamiento Multi-Tenant**: Ninguna consulta DEBE omitir el filtro `tenant_id`.

---

## 9. Casos Límite y Manejo de Errores

* **Concurrencia en Ventas**: Si dos vendedores procesan simultáneamente el último producto en stock, la primera venta se efectúa y la segunda se rechaza por stock insuficiente.
* **Intento de Borrado de Producto con Ventas**: El sistema impide la eliminación física y sugiere cambiar el estado a `inactivo`.
* **Acceso por Rol Vendedor a Usuarios/Resumen**: El backend responde con error 403 Forbidden.

---

## 10. Seguridad, Aislamiento y Permisos

* Autenticación basada en sesiones/tokens seguros fijados al `tenant_id`.
* Control de acceso RBAC backend:
  * `Administrador`: Acceso total.
  * `Vendedor`: Acceso a Ventas, Compras, Productos, Clientes e Inventario. Denegado en Usuarios y Resumen del Negocio.

---

## 11. Auditoría e Historial de Eventos

* Registro inmutable de ventas, compras e ingresos/egresos de mercancía con ID de usuario y marca de tiempo.

---

## 12. Búsqueda y Filtros

* Búsqueda por SKU o nombre en productos.
* Búsqueda por nombre o documento en clientes.
* Filtrado de ventas por cliente o fecha.

---

## 13. Gestión de Productos (Reglas Específicas)
* Inactivación lógica si el producto posee historial en ventas o compras. Borrado físico solo si no tiene registros asociados.

## 14. Gestión de Clientes (Reglas Específicas)
* Inactivación lógica para preservar historial comercial. Inclusión de cliente genérico por defecto ("Consumidor Final").

## 15. Gestión de Ventas (Reglas Específicas)
* Operación atómica e inmutable. Descuento automático de existencias.

## 16. Gestión de Compras (Reglas Específicas)
* Registro por producto, cantidad y costo unitario sin entidad proveedor. Incremento automático de existencias.

## 17. Gestión de Inventario (Reglas Específicas)
* Stock consolidado derivado exclusivamente de transacciones de `VENTA` y `COMPRA`.

## 18. Resumen del Negocio (Reglas Específicas)
* Exclusivo para rol `Administrador`. Muestra total vendido, número de ventas y conteos clave aislados por *tenant*.

---

## 23. Requisitos de Ciberseguridad, Calidad y Estrategia de Pruebas Automatizadas

### 23.1 Alcance y Estrategia de Pruebas Automatizadas
El proceso de validación y aseguramiento de calidad de Arus ERP DEBE contar con una suite de pruebas automatizadas estructurada en tres niveles:

1. **Pruebas Unitarias (Backend & Frontend)**:
   - Validación de lógica de negocio aislada (cálculo de subtotales y totales monetarios con precisión exacta, funciones de validación de modelos y esquemas DTO).
   - Generación de hashes criptográficos de contraseñas (`bcrypt`) y creación/decodificación de tokens JWT.
2. **Pruebas de Integración y Persistencia (Backend + Database)**:
   - Verificación de la capa de persistencia asíncrona (operaciones CRUD en PostgreSQL).
   - Pruebas atómicas de transacciones comerciales: descuento de stock en ventas, adición de stock en compras y registro inmutable en `inventory_movements`.
   - Pruebas de control de concurrencia y bloqueo de filas (`SELECT ... FOR UPDATE`).
   - Pruebas automatizadas de **Aislamiento Multi-Tenant**: verificación de que ejecuciones en contexto de `Tenant_A` no retornen jamás registros pertenecientes a `Tenant_B`.
3. **Pruebas de Contrato y Rutas de API (Backend Endpoints)**:
   - Verificación de contratos OpenAPI / JSON Schema en endpoints REST.
   - Validación de respuestas ante tokens ausentes, caducados o alterados (HTTP 401 Unauthorized).
   - Validación de reglas de autorización RBAC (HTTP 403 Forbidden para usuarios `SELLER` al intentar consumir `/users` o `/dashboard/summary`).

---

### 23.2 Matriz de Escenarios de Prueba (Casos Exitosos y Casos de Error)

Las pruebas automatizadas DEBEN validar explícitamente tanto el comportamiento esperado (camino feliz) como el manejo seguro ante errores y casos límite para cada una de las 10 HUs:

| ID Escenario | HU Relacionada | Tipo de Caso | Descripción del Escenario de Prueba | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| **TC-001** | HU-001 | Exitoso | Registro de empresa con NIT y correo válidos no existentes. | Retorna HTTP 201, crea el `Tenant`, registra el usuario `Administrador` y genera token JWT inicial. |
| **TC-002** | HU-001 | Error | Registro de empresa con NIT o correo electrónico ya existente. | Retorna HTTP 400 Bad Request indicando duplicidad sin crear registros parciales en base de datos. |
| **TC-003** | HU-002 | Exitoso | Autenticación con correo y contraseña correctas. | Retorna HTTP 200 OK y token JWT firmado con claims válidos (`sub`, `tenant_id`, `role_id`). |
| **TC-004** | HU-002 | Error | Intento de login con contraseña incorrecta o usuario inactivo. | Retorna HTTP 401 Unauthorized con mensaje genérico de credenciales inválidas. |
| **TC-005** | HU-003 | Exitoso | Administrador crea colaborador con rol `SELLER` o `ADMIN`. | Retorna HTTP 201 y el usuario queda registrado bajo el `tenant_id` del Administrador autenticado. |
| **TC-006** | HU-003 | Error / RBAC | Usuario con rol `SELLER` intenta consultar `GET /users` o crear usuario. | Retorna HTTP 403 Forbidden bloqueando la ejecución. |
| **TC-007** | HU-004 | Exitoso | Registro de producto con SKU único, precio y stock mayor o igual a 0. | Retorna HTTP 201 y guarda el producto activo en el catálogo del tenant. |
| **TC-008** | HU-004 | Límite / Soft-Delete | Inactivación de producto que posee historial transaccional de ventas/compras. | Retorna HTTP 200 marcando `status = INACTIVE`. El producto no se elimina de la base de datos. |
| **TC-009** | HU-005 | Exitoso | Creación de cliente y consulta de cliente genérico "Consumidor Final". | El cliente por defecto está disponible para ventas sin requerir datos adicionales. |
| **TC-010** | HU-008 | Exitoso | Registro de compra notificando lista de productos, cantidades y costo unitario. | Transacción atómica: retorna HTTP 201, incrementa el stock de cada producto y registra `movement_type = PURCHASE`. |
| **TC-011** | HU-006 | Exitoso | Registro de venta atómica con productos con stock suficiente. | Transacción atómica: calcula sub-totales exactos, descuenta el stock, registra la venta inmutable y crea `inventory_movements`. |
| **TC-012** | HU-006 | Error / Stock | Venta de producto solicitando cantidad mayor al stock disponible en almacén. | Retorna HTTP 400 Bad Request indicando stock insuficiente. Ningún producto descuenta existencias ni se crea la venta. |
| **TC-013** | HU-006 | Concurrencia | Dos solicitudes de venta simultáneas sobre la última unidad de producto. | La primera solicitud adquiere el bloqueo pesimista y se confirma; la segunda se rechaza limpiamente por stock insuficiente. |
| **TC-014** | HU-007 | Exitoso / Inmutabilidad | Consulta de historial de ventas y detalle de recibos confirmados. | Retorna la lista ordenada. Ningún endpoint de la API permite modificar o borrar ventas pasadas. |
| **TC-015** | HU-009 | Exitoso | Consulta de existencias consolidadas por producto. | Muestra el `current_stock` derivado exactamente de la suma de compras menos ventas. |
| **TC-016** | HU-010 | Exitoso | Administrador consulta resumen del negocio (`/dashboard/summary`). | Retorna la suma total vendida y conteos agregados filtrados estrictamente por el `tenant_id` autenticado. |
| **TC-017** | Security | Isolation | Consulta de productos/ventas de Tenant A autenticado con token de Tenant B. | Tenant B recibe un array vacío o error 404; cero visibilidad de la información de Tenant A. |

---

### 23.3 Validaciones de Ciberseguridad e Información Sensible

Las siguientes validaciones de seguridad DEBEN ser aplicadas y verificadas de manera automatizada en el sistema:

* **SEC-001: Sanitización y Validación de Entradas**:
  - Toda entrada de usuario (JSON Payloads, Query Parameters, Headers) DEBE validarse contra esquemas estrictos de tipo, longitud y rango (Pydantic / JSON Schema).
  - Rechazar cadenas maliciosas de inyección SQL mediante la parametrización obligatoria de consultas ORM/SQL asíncronas.
  - Escapar y desinfectar valores en respuestas frontend para prevenir Cross-Site Scripting (XSS).
* **SEC-002: Almacenamiento Seguro de Credenciales**:
  - Las contraseñas de usuario DEBEN ser procesadas con un hash criptográfico robusto (`bcrypt` con factor de trabajo adecuado) antes de ser guardadas en la base de datos.
  - Prohibición absoluta de almacenar o transmitir contraseñas en texto plano.
* **SEC-003: Autenticación Basada en Tokens JWT Seguros**:
  - La autenticación DEBE valerse de tokens JWT firmados con clave secreta criptográfica (algoritmo HS256 o superior).
  - Los tokens DEBEN incluir claims obligatorios de expiración (`exp`), identidad del usuario (`sub`), `tenant_id` y `role_id`.
  - Todo token expirado, malformado o con firma alterada DEBE ser rechazado de inmediato con HTTP 401 Unauthorized.
* **SEC-004: Autorización RBAC en Backend (Server-Side Enforcement)**:
  - Las reglas de autorización DEBEN evaluarse exclusivamente en el backend (guardias de dependencia o decoradores de endpoint). La UI frontend solo se considera una capa de conveniencia visual.
  - Endpoints restringidos (`/users` y `/dashboard/summary`) DEBEN retornar HTTP 403 Forbidden ante cualquier token con `role_id == 'SELLER'`.
* **SEC-005: Aislamiento Cero-Fugas Multi-Tenant (Multi-Tenant Scope)**:
  - Ninguna consulta a la base de datos que acceda a entidades asociadas a empresa (usuarios, productos, clientes, ventas, compras, inventario) DEBE ejecutarse sin filtrar explícitamente por `tenant_id == current_authenticated_tenant`.
  - El `tenant_id` DEBE extraerse únicamente del token JWT verificado en el servidor, nunca desde parámetros de URL o payloads enviables por el cliente.
* **SEC-006: Protección de Información Sensible y Sanitización de Errores**:
  - Los mensajes de error devueltos por la API DEBEN ser informativos pero genéricos (ejemplo: "Credenciales inválidas" en lugar de "Usuario no encontrado" o "Contraseña errónea").
  - En entornos de producción, las respuestas de error NO DEBEN exponer trazas de pila (stack traces), estructuras internas de base de datos ni firmas del framework.
  - Las respuestas de consulta de usuario NUNCA DEBEN incluir el campo `password_hash`.
* **SEC-007: Control de Concurrencia y Resiliencia**:
  - El registro de ventas DEBE hacer uso de bloqueos pesimistas de fila (`SELECT ... FOR UPDATE`) sobre las entidades `Product` dentro de la transacción activa para prevenir condiciones de carrera en ventas simultáneas.

---

### 23.4 Criterios de Aceptación de Calidad y Correcto Funcionamiento (QA Gate)

Para considerar el proceso de Arus ERP correctamente probado y listo para paso a producción, se DEBEN cumplir los siguientes criterios objetivamente verificables:

* **QA-001 (Cobertura de Pruebas Automatizadas)**: La suite de pruebas automatizadas (unitarias + integración + API) DEBE cubrir como mínimo el **80% de las líneas de código** en los módulos de lógica de negocio, autenticación, ventas e inventario.
* **QA-002 (Pruebas de Aislamiento Multi-Tenant Pasar 100%)**: El 100% de las pruebas automatizadas de aislamiento de datos entre empresas DEBEN pasar exitosamente en verde sin una sola falla.
* **QA-003 (Pruebas de Atomicidad y Concurrencia Pasar 100%)**: Las pruebas de registro de venta, descuento de stock y rechazo por stock insuficiente DEBEN pasar al 100%.
* **QA-004 (Verificación de Inmutabilidad)**: No debe existir ningún endpoint ni función en el sistema que permita la actualización o eliminación de registros en las tablas `sales` o `inventory_movements`.
* **QA-005 (Formato de Respuestas de Error)**: El 100% de las respuestas ante fallos de validación o seguridad DEBEN ser JSON estructurados con código de estado HTTP adecuado (400, 401, 403, 404, 422).
* **QA-006 (Definition of Done)**: Una Historia de Usuario se considera completamente probada únicamente cuando:
  1. Los escenarios de aceptación funcionales ( Given / When / Then ) tienen pruebas automatizadas asociadas.
  2. Los casos de error y límite aplicables cuentan con aserciones automatizadas de rechazo seguro.
  3. No se detectan regresiones en las historias previamente integradas.

---

## 19. Trazabilidad

| Necesidad de Negocio | Historia de Usuario | Requisito Funcional | Requisito de Seguridad / Calidad | Criterio de Éxito |
| :--- | :--- | :--- | :--- | :--- |
| Registro de empresa y multi-tenant | HU-001 | FR-001, FR-017 | SEC-001, SEC-005, TC-001, TC-002 | SC-001, SC-002, QA-002 |
| Autenticación y Seguridad | HU-002 | FR-002, FR-004 | SEC-002, SEC-003, SEC-006, TC-003, TC-004 | SC-002, QA-001 |
| Gestión de Colaboradores y Roles | HU-003 | FR-003, FR-004, FR-005 | SEC-004, TC-005, TC-006 | SC-002, QA-001 |
| Catálogo e Inventario | HU-004, HU-009 | FR-006, FR-014 | SEC-001, TC-007, TC-008, TC-015 | SC-005, QA-001 |
| Gestión de Clientes | HU-005 | FR-007, FR-008 | SEC-001, TC-009 | SC-005, QA-001 |
| Ventas, Concurrencia e Inmutabilidad | HU-006, HU-007 | FR-009, FR-010, FR-011, FR-012 | SEC-007, TC-011, TC-012, TC-013, TC-014 | SC-003, SC-004, SC-006, QA-003, QA-004 |
| Abastecimiento / Compras | HU-008 | FR-013, FR-016 | SEC-007, TC-010 | SC-006, QA-003 |
| Resumen del Negocio | HU-010 | FR-015 | SEC-004, SEC-005, TC-016 | SC-005, QA-001 |
| Aislamiento Global & QA Gate | Cross | FR-016, FR-017 | SEC-005, QA-001 a QA-006, TC-017 | SC-002, SC-007, QA-001 a QA-006 |

---

## 20. Success Criteria *(mandatory)*

* **SC-001**: Registro de empresa y acceso inicial completado en menos de 2 minutos.
* **SC-002**: 100% de aislamiento verificado entre datos de diferentes *tenants*.
* **SC-003**: Transacción de venta y descuento de stock ejecutada en menos de 3 segundos.
* **SC-004**: 100% de exactitud en cálculos de totales y subtotales monetarios.
* **SC-005**: Un usuario sin experiencia previa completa exitosamente el flujo básico secuencial de registrar un producto, registrar un cliente y realizar una venta durante una sesión de prueba guiada sin requerir asistencia técnica externa.
* **SC-006**: Trazabilidad e historial de auditoría inmutable en el 100% de las ventas y compras.
* **SC-007**: 100% de las pruebas automatizadas de ciberseguridad, aislamiento multi-tenant, atómicas y de control de concurrencia aprobadas sin fallas.

---

## 21. Assumptions

* Aplicación web conectada (sin soporte *Offline-First* en v1).
* Navegadores web modernos en escritorio, tabletas y dispositivos móviles.
* Moneda local única por empresa en v1.0.0.

---

## 22. Restricciones de la Especificación

> [!IMPORTANT]
> **Delimitación de Alcance de la Especificación**:
> Esta especificación define exclusivamente **QUÉ** debe hacer el producto Arus ERP y **POR QUÉ** es necesario para el negocio, incluyendo formalmente los requisitos de **Ciberseguridad, Calidad y Estrategia de Pruebas Automatizadas (Sección 23)**. **NO define aún la implementación de código**. Las decisiones técnicas concretas de frameworks de testing (pytest, Vitest, Playwright) o arquitectura específica se derivan posteriormente respetando siempre la [Constitution](file:///c:/Users/ioavm/OneDrive/Escritorio/IOAV/Arus/.specify/memory/constitution.md).
