# Feature Specification: Demo Day Enhancements

**Feature Branch**: `002-demo-day-enhancements`

**Created**: 2026-08-21

**Status**: Draft

**Input**: User description: "Cuatro nuevas Historias de Usuario (HU-011 a HU-014) que extienden la línea base funcional de Arus ERP (001-initial-baseline, HU-001 a HU-010) para el Demo Day: indicador de stock mínimo, filtro del historial de ventas por cliente/fecha, categorías de producto, y cambio de contraseña propia. Las cuatro deben ser incrementos independientes, asignables al azar a cuatro integrantes distintos, cada uno desarrollando en su propia rama sin depender de que otra historia esté terminada primero."

**Baseline de referencia**: [001-initial-baseline/spec.md](../001-initial-baseline/spec.md) — esta especificación **extiende** el sistema ya construido; no reemplaza ni modifica ninguna de las HU-001 a HU-010 existentes.

**Independencia y prioridad**: Las cuatro historias (HU-011, HU-012, HU-013, HU-014) comparten la misma prioridad (P1) para el Demo Day. Se asignarán al azar entre los cuatro integrantes del equipo; cada una puede iniciarse de inmediato, ninguna depende de que otra esté terminada primero, y las cuatro parten exactamente del mismo estado actual de `001-initial-baseline` ya desplegado.

## User Scenarios & Testing *(mandatory)*

<!--
  Las cuatro historias (HU-011 a HU-014) son incrementos de evolución independientes sobre
  módulos ya operativos del baseline (001-initial-baseline). Se asignan al azar entre los
  cuatro integrantes durante el Demo Day, por lo que las CUATRO comparten la misma prioridad
  (P1): ninguna es más importante ni más urgente que otra, ninguna requiere que otra esté
  terminada primero, y las cuatro parten exactamente del mismo estado actual del baseline
  ya desplegado. Cada una es independientemente desarrollable, probable, desplegable y
  demostrable por separado.
-->

### User Story 1 - Filtrar historial de ventas por cliente y fecha (Priority: P1)

Como usuario autorizado (Administrador o Vendedor), quiero filtrar el historial de ventas por cliente y por rango de fechas, para encontrar rápidamente las operaciones que necesito consultar sin recorrer todo el historial.

**Extiende**: HU-007 (Consultar ventas) del baseline. Es una capacidad de solo lectura añadida sobre el historial de ventas ya existente; no crea, modifica ni elimina ninguna venta.

**Why this priority**: Tiene alto valor de uso diario por sí sola (cualquier negocio con más de unas pocas ventas necesita poder buscarlas) y es completamente autocontenida: no depende de ningún dato ni cambio introducido por HU-011, HU-013 o HU-014.

**Independent Test**: Con al menos dos clientes y ventas registradas en fechas distintas, aplicar un filtro por un cliente específico y verificar que solo aparecen sus ventas; aplicar un rango de fechas y verificar que se excluyen las ventas fuera del rango; combinar ambos filtros y verificar la intersección correcta.

**Acceptance Scenarios**:

1. **Given** existen ventas de varios clientes en el historial, **When** el usuario filtra por un cliente específico, **Then** el listado muestra únicamente las ventas de ese cliente, ordenadas de la más reciente a la más antigua.
2. **Given** existen ventas registradas en distintas fechas, **When** el usuario aplica un rango de fecha inicio y fecha fin, **Then** el listado muestra únicamente las ventas cuya fecha de registro cae dentro del rango (incluyendo los extremos).
3. **Given** el usuario combina filtro de cliente y rango de fechas, **When** aplica ambos a la vez, **Then** el listado refleja la intersección exacta de ambas condiciones.
4. **Given** el usuario no aplica ningún filtro, **When** consulta el historial, **Then** el comportamiento es idéntico al existente hoy (todas las ventas del negocio, de la más reciente a la más antigua).
5. **Given** un usuario intenta filtrar por un cliente que pertenece a otra empresa (tenant), **When** aplica el filtro, **Then** el resultado es una lista vacía — nunca se revela información de otra empresa.

---

### User Story 2 - Indicador de stock mínimo (Priority: P1)

Como administrador o vendedor, quiero definir un stock mínimo para cada producto y visualizar cuáles están por debajo de ese límite, para detectar oportunamente productos que necesitan reposición.

**Extiende**: HU-004 (Gestionar productos) y HU-009 (Consultar inventario) del baseline. Añade un dato de configuración por producto y un indicador visual en la consulta ya existente de inventario.

**Why this priority**: Tiene alto valor operativo por sí sola (evita quiebres de stock) y es completamente autocontenida: agrega un dato nuevo por producto y una regla de visualización, sin depender de HU-012, HU-013 ni HU-014.

**Independent Test**: Crear o editar un producto asignándole un stock mínimo mayor a su existencia actual, y verificar que aparece marcado como "Stock bajo" en la consulta de inventario; aumentar la existencia por encima del mínimo y verificar que la marca desaparece.

**Acceptance Scenarios**:

1. **Given** un usuario está creando o editando un producto, **When** especifica un valor de stock mínimo, **Then** el sistema lo guarda asociado a ese producto (si no se especifica al crear, el valor por defecto es cero).
2. **Given** un producto tiene una existencia actual menor que su stock mínimo configurado, **When** se consulta el listado de inventario, **Then** ese producto se muestra con un indicador visual de "Stock bajo".
3. **Given** un producto tiene existencia igual o mayor que su stock mínimo, **When** se consulta el inventario, **Then** no muestra el indicador de "Stock bajo".
4. **Given** el stock mínimo está configurado, **When** se registra una venta o compra sobre ese producto, **Then** el registro de la transacción ocurre exactamente igual que hoy (el stock mínimo es puramente informativo y nunca bloquea ni condiciona una venta o compra).
5. **Given** el sistema evalúa el indicador de stock bajo, **When** ocurre esta evaluación, **Then** es un cálculo mostrado únicamente al consultar la pantalla — el sistema NO envía correos, notificaciones push, ni ejecuta ningún proceso en segundo plano por este motivo (exclusión explícita heredada del baseline).

---

### User Story 3 - Categorías de productos (Priority: P1)

Como administrador o vendedor, quiero clasificar los productos mediante categorías, para organizar mejor el catálogo y facilitar su consulta.

**Extiende**: HU-004 (Gestionar productos) del baseline, como una extensión aislada y opcional del catálogo.

**Why this priority**: Aporta valor organizativo por sí sola (más relevante cuanto más crece el catálogo) y es completamente autocontenida: introduce una entidad nueva (categoría) y una relación opcional con producto, sin depender de HU-011, HU-012 ni HU-014.

**Independent Test**: Crear una categoría, asociarla a un producto nuevo o existente, y verificar que la categoría se refleja correctamente al consultar ese producto; verificar que un producto sin categoría asignada sigue funcionando con total normalidad en ventas, compras e inventario.

**Acceptance Scenarios**:

1. **Given** un usuario autorizado desea organizar el catálogo, **When** crea una categoría con un nombre, **Then** el sistema la guarda y queda disponible para asociarse a productos de su misma empresa.
2. **Given** existen categorías creadas, **When** el usuario las consulta, **Then** ve el listado de categorías de su empresa (nunca las de otra empresa).
3. **Given** un usuario está creando o editando un producto, **When** selecciona una categoría existente de su empresa, **Then** el producto queda asociado a esa categoría y esta se refleja al consultarlo.
4. **Given** un producto no tiene categoría asignada, **When** se opera sobre él (venta, compra, consulta de inventario), **Then** funciona exactamente igual que cualquier otro producto — la categoría es completamente opcional y no afecta ninguna regla de negocio existente.
5. **Given** un usuario intenta crear una categoría con un nombre ya usado en su misma empresa, **When** envía la solicitud, **Then** el sistema la rechaza con un mensaje claro (mismo patrón que el usado hoy para SKU o correo duplicado).

---

### User Story 4 - Cambio de contraseña propia (Priority: P1)

Como usuario autenticado, quiero cambiar mi propia contraseña, para mantener segura mi cuenta sin depender de un administrador.

**Extiende**: HU-002 (Iniciar sesión) y HU-003 (Gestionar usuarios) del baseline — reutiliza el mecanismo de autenticación ya establecido en HU-002 y complementa la gestión de cuentas de HU-003 con una vía de autoservicio para el propio usuario, sin sustituir ni modificar la gestión administrativa existente.

**Why this priority**: Es una mejora de higiene de seguridad valiosa por sí sola (autonomía del usuario sin depender de un administrador) y es completamente autocontenida: no depende de HU-011, HU-012 ni HU-013.

**Independent Test**: Autenticarse, cambiar la contraseña propia indicando correctamente la contraseña actual, cerrar sesión, iniciar sesión con la nueva contraseña (debe funcionar) y luego intentar con la anterior (debe ser rechazada).

**Acceptance Scenarios**:

1. **Given** un usuario ha iniciado sesión, **When** solicita cambiar su contraseña indicando su contraseña actual correctamente y una nueva contraseña válida, **Then** el sistema actualiza su contraseña de acceso.
2. **Given** un usuario intenta cambiar su contraseña, **When** la contraseña actual indicada es incorrecta, **Then** el sistema rechaza la operación con un mensaje genérico, sin revelar detalles internos.
3. **Given** la contraseña fue cambiada exitosamente, **When** el usuario intenta iniciar sesión nuevamente, **Then** solo la nueva contraseña permite el acceso; la anterior queda inválida de inmediato.
4. **Given** la nueva contraseña no cumple las reglas mínimas de seguridad ya vigentes en el sistema (las mismas usadas al registrar una empresa o al crear un colaborador), **When** el usuario la envía, **Then** el sistema la rechaza indicando el motivo.
5. **Given** un usuario no ha iniciado sesión, **When** intenta acceder a esta función, **Then** el sistema la deniega — la operación requiere sesión autenticada y solo permite modificar la contraseña de la propia cuenta (nunca la de otro usuario, ni siquiera para un Administrador).

---

### Edge Cases

- ¿Qué ocurre si el usuario aplica un rango de fechas donde la fecha de inicio es posterior a la fecha de fin? El sistema debe devolver una lista vacía, no un error (US1).
- ¿Qué ocurre si se filtra el historial de ventas por un identificador de cliente que no existe? El sistema debe devolver una lista vacía, no un error de "no encontrado" (US1).
- ¿Qué ocurre si se intenta configurar un stock mínimo negativo? Debe rechazarse con el mismo tipo de validación ya usada para la existencia y el precio de un producto (US2).
- ¿Qué ocurre con los productos que ya existen en el sistema antes de esta mejora (sin stock mínimo definido)? Deben tratarse como si su stock mínimo fuera cero, sin requerir ninguna acción manual de migración de datos (US2).
- ¿Qué ocurre si se intenta asociar un producto a una categoría que pertenece a otra empresa o que no existe? Debe rechazarse con un mensaje claro, igual que hoy ocurre al intentar vender a un cliente inválido (US3).
- ¿Qué ocurre con los productos que ya existen antes de esta mejora (sin categoría asignada)? Deben seguir operando con total normalidad, mostrándose como "sin categoría" (US3).
- ¿Qué ocurre si un usuario intenta cambiar la contraseña de otra cuenta? No es posible: la identidad del usuario a modificar siempre se determina por su sesión activa, nunca por un dato enviado en la solicitud (US4).
- ¿Qué ocurre si la nueva contraseña es igual a la actual? Se acepta (no hay una prohibición explícita de reutilización en el baseline); no se introduce una regla nueva no solicitada.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir filtrar el historial de ventas por un cliente específico de la misma empresa. *(US1 — extiende HU-007)*
- **FR-002**: El sistema DEBE permitir filtrar el historial de ventas por un rango de fechas (inicio y fin, ambos opcionales e independientes entre sí). *(US1 — extiende HU-007)*
- **FR-003**: El sistema DEBE permitir combinar el filtro de cliente y el filtro de fecha simultáneamente, y DEBE preservar el orden de más reciente a más antigua y el aislamiento por empresa ya vigentes. *(US1 — extiende HU-007)*
- **FR-004**: El sistema DEBE permitir definir y actualizar un valor de stock mínimo por producto, con un valor por defecto de cero cuando no se especifica. *(US2 — extiende HU-004)*
- **FR-005**: El sistema DEBE mostrar un indicador visual cuando la existencia actual de un producto sea menor que su stock mínimo configurado, sin generar notificaciones, correos ni ejecutar procesos automáticos de ningún tipo. *(US2 — extiende HU-009)*
- **FR-006**: El stock mínimo NO DEBE alterar ni condicionar el registro de ventas o compras existente; es exclusivamente informativo. *(US2)*
- **FR-007**: El sistema DEBE permitir crear categorías de producto con un nombre único dentro de cada empresa, y consultarlas en una lista. *(US3 — extiende HU-004)*
- **FR-008**: El sistema DEBE permitir asociar de forma opcional un producto a una categoría existente de la misma empresa. *(US3 — extiende HU-004)*
- **FR-009**: Un producto sin categoría asignada DEBE seguir siendo completamente funcional en ventas, compras e inventario, sin excepciones ni pasos adicionales. *(US3)*
- **FR-010**: El sistema DEBE permitir a un usuario autenticado cambiar su propia contraseña, exigiendo y validando la contraseña actual antes de aplicar el cambio. *(US4 — extiende HU-002)*
- **FR-011**: El cambio de contraseña DEBE aplicar las mismas reglas mínimas de seguridad ya vigentes en el sistema para contraseñas nuevas, y DEBE reutilizar el mismo mecanismo de protección de contraseñas ya usado en el resto del sistema (sin introducir uno nuevo). *(US4)*
- **FR-012**: El cambio de contraseña propia NO DEBE alterar el rol, el estado de la cuenta, ni el flujo de inicio de sesión existente, y DEBE limitarse exclusivamente a la cuenta del usuario autenticado que la solicita (nunca la de otro usuario). *(US4)*

### Key Entities *(include if feature involves data)*

- **Producto** *(entidad existente del baseline, extendida)*: se le añaden dos atributos opcionales de configuración — un umbral de **stock mínimo** (US2) y una referencia opcional a **Categoría** (US3). Ninguno de los dos es obligatorio; los productos existentes siguen siendo válidos sin ellos.
- **Categoría** *(entidad nueva)*: representa una clasificación del catálogo, identificada por un nombre único dentro de cada empresa. Pertenece a una única empresa (aislamiento por tenant) y puede estar asociada a cero, uno o varios productos.
- **Venta** *(entidad existente del baseline, sin cambios de datos)*: US1 solo añade nuevas formas de consultarla (por cliente y por fecha); no se agregan, quitan ni modifican atributos, y su inmutabilidad ya establecida se mantiene intacta.
- **Usuario** *(entidad existente del baseline, sin cambios de datos)*: US4 solo permite actualizar el valor ya existente de la credencial de acceso de la propia cuenta; no se agregan atributos nuevos ni se modifica el modelo de roles.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un usuario puede encontrar las ventas de un cliente específico dentro de un rango de fechas concreto, sin tener que revisar manualmente el resto del historial, en el 100% de los casos probados.
- **SC-002**: Un producto cuya existencia cae por debajo de su umbral configurado es identificable visualmente por el usuario en el mismo momento en que consulta el inventario, sin ninguna acción ni espera adicional.
- **SC-003**: Un usuario puede organizar y encontrar productos agrupados por categoría, y los productos sin categoría asignada continúan operando en ventas, compras e inventario sin ninguna interrupción o error.
- **SC-004**: Un usuario puede actualizar su propia contraseña y autenticarse exitosamente con ella de inmediato; la contraseña anterior deja de funcionar en el 100% de los casos.

## Assumptions

- El equipo de trabajo está compuesto por 4 integrantes, cada uno implementando una de las cuatro historias en su propia rama, partiendo del estado actual de la línea base (001-initial-baseline) ya desplegada.
- La asignación de historia a integrante es aleatoria y puede cambiar en cualquier momento; por eso ninguna historia asume conocimiento previo de quién implementa las otras tres, ni depende de que otra esté terminada.
- Las reglas mínimas de seguridad para contraseñas (US4) son las mismas ya vigentes en el sistema para el registro de empresa y la creación de colaboradores — no se define un estándar nuevo.
- La edición y el borrado de categorías, así como las categorías jerárquicas (subcategorías), quedan fuera de alcance de esta iteración; solo se requiere crear y listar.
- El filtro de historial de ventas (US1) se limita a cliente y rango de fechas, tal como fue solicitado; no incluye filtro por monto, producto ni vendedor.
- La recuperación de contraseña olvidada (sin sesión activa) queda fuera de alcance; US4 cubre únicamente el cambio autenticado de una contraseña conocida.
- Ninguna de las cuatro historias requiere un rol nuevo ni una reestructuración del modelo de permisos ya vigente (Administrador / Vendedor); todas operan bajo el mismo nivel de acceso ya definido para el módulo que extienden.
