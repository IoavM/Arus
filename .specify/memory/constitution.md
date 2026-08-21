<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.0.1 (PATCH: Clarifications to Clarify stage optionality, API protocol flexibility, and Git branching guidance)
- Modified principles: Principle III (API protocol flexibility), Principle XII (Git branching flexibility for minor tasks)
- Added sections: N/A
- Removed sections: N/A
- Follow-up TODOs: None
-->

# Arus ERP Constitution

## Core Principles

### I. Priorización del Usuario (Usabilidad sobre Complejidad sin Sacrificar Seguridad)
La jerarquía de prioridades del proyecto Arus es estrictamente la siguiente:
1. Usabilidad y Experiencia de Usuario (UX)
2. Correctitud, Integridad de Datos y Seguridad
3. Modularidad y Mantenibilidad
4. Escalabilidad
5. Rendimiento

La simplicidad operativa DEBE ser prioritaria frente a la complejidad técnica innecesaria. No obstante, NUNCA se sacrificará la seguridad, la integridad de los datos ni la confiabilidad transaccional con el fin de simplificar una implementación.

### II. UX Simple, Consistente y Accesible
La interfaz de usuario (UI) DEBE:
* Emplear lenguaje de negocio claro y accesible para usuarios no técnicos de PYMEs y micronegocios, evitando jerga contable o técnica innecesaria.
* Mantener flujos operativos cotidianos tan cortos y directos como sea razonablemente posible.
* Garantizar consistencia visual, de interacción y de estado en todos los módulos.
* Prevenir errores del usuario mediante validaciones en tiempo real y confirmaciones para acciones destructivas.
* Ser completamente adaptativa (*responsive*) para escritorio, tabletas y dispositivos móviles.
* Incorporar divulgación progresiva (*progressive disclosure*) para funcionalidades avanzadas con el fin de no sobrecargar la UI inicial.

*Regla de diseño*: No se impondrán reglas rígidas artificiales (ej. "máximo 3 clics") si perjudican la claridad o seguridad. PWA y enfoque *Mobile-First* no son requisitos obligatorios iniciales.

### III. Arquitectura Monolito Modular y Extensible
Arus DEBE estructurarse inicialmente como un **Monolito Modular**:
* Los módulos backend DEBE poseer responsabilidades delimitadas, alta cohesión y bajo acoplamiento.
* La incorporación de nuevos módulos funcionales NO DEBE requerir modificaciones invasivas en los módulos existentes.
* El frontend (React) DEBE organizarse en una estructura modular con componentes reutilizables y desacoplados.
* La comunicación entre el frontend y el backend DEBE realizarse mediante APIs con contratos explícitos y mecanismos de comunicación claramente definidos.
* Queda prohibido adoptar microservicios, arquitecturas de plugins o sistemas distribuidos de forma prematura; cualquier cambio de este tipo requerirá justificación formal en fases posteriores de Plan.

### IV. Seguridad desde el Diseño (Security by Design)
La seguridad es una responsabilidad transversal no negociable:
* Secretos, claves de API, credenciales de base de datos y tokens privados NUNCA DEBEN incluirse en el código del frontend ni exponerse al navegador.
* Toda variable expuesta al frontend DEBE considerarse pública.
* La autenticación y autorización DEBEN validarse obligatoriamente en el backend; el frontend NUNCA será la única barrera de seguridad.
* Todo dato recibido por el backend DEBE ser validado independientemente de las validaciones hechas en el cliente.
* Las contraseñas NUNCA DEBEN almacenarse en texto plano y DEBE aplicarse el principio de mínimo privilegio en todos los componentes.
* Los mensajes de error expuestos al usuario NUNCA DEBEN revelar *stack traces*, credenciales ni detalles de infraestructura.

### V. Multi-tenancy Nativo y Aislamiento de Datos
Arus NACE como una aplicación **multi-tenant** desde su versión 1.0.0:
* Cada empresa (*tenant*) DEBE mantener sus datos aislados de forma estricta e inequívoca respecto a otros *tenants*.
* El backend DEBE resolver el contexto del *tenant* a partir del token o sesión autenticada, NUNCA confiando ciegamente en identificadores enviados libremente por el cliente.
* PostgreSQL DEBE proporcionar mecanismos adicionales de protección a nivel de persistencia para evitar accesos cruzados entre *tenants*.
* Las relaciones de datos entre distintos *tenants* están estrictamente PROHIBIDAS.

### VI. Modelo de Autorización Declarativo
El modelo de permisos DEBE responder a la jerarquía conceptual: **Usuario → Tenant → Rol → Permisos**.
* El backend DEBE verificar la autorización en cada solicitud a endpoints protegidos.
* El frontend podrá ocultar elementos visuales según los permisos del usuario, pero esto constituye una mejora de UX, NO un mecanismo de seguridad.
* El sistema DEBE permitir la adición de nuevos roles y permisos sin requerir reestructuraciones de la base de datos o del código.

### VII. Integridad Transaccional y Consistencia de Datos
La exactitud de la información empresarial es prioritaria:
* Las reglas de negocio críticas DEBEN ser validadas y ejecutadas en el backend y reforzadas mediante restricciones nativas en PostgreSQL.
* Las operaciones compuestas DEBEN ejecutarse dentro de transacciones atómicas (ACID).
* Los registros de historial empresarial (facturas, ventas, movimientos) NO DEBEN eliminarse físicamente cuando se destruya trazabilidad; se utilizarán mecanismos de anulación o inactivación lógica.
* Los valores monetarios DEBEN representarse con tipos de datos de precisión exacta (evitando punto flotante).
* Los cálculos de negocio y el control de operaciones concurrentes DEBEN gestionarse centralizadamente en el backend.

### VIII. Auditoría y Trazabilidad Empresarial Inmutable
Las operaciones críticas (creación, modificación, anulación o eliminación de registros financieros, contables o de inventario) DEBEN registrar trazabilidad inmutable que identifique:
1. Quién realizó la operación (*Usuario / Actor*).
2. Cuándo ocurrió (*Timestamp ISO 8601*).
3. Qué entidad y registro fueron afectados (*Entidad / ID*).
4. Qué operación específica se ejecutó (*Acción / Cambio de estado*).

No es obligatorio auditar lecturas o interacciones triviales de navegación.

### IX. Calidad Automatizada y Pruebas Relevantes
Las pruebas automatizadas son obligatorias y forman parte del ciclo continuo de desarrollo:
* Ninguna funcionalidad se considerará terminada si sus pruebas asociadas no son satisfactorias.
* Las pruebas DEBEN derivarse de los criterios de aceptación especificados en las historias.
* Las reglas de negocio críticas DEBEN contar con pruebas unitarias y de integración backend/API.
* Se evitará perseguir métricas artificiales de porcentaje de cobertura; la calidad se medirá por la relevancia y capacidad de los tests para detectar fallos reales.

### X. SDD como Mecanismo Estricto de Control del Desarrollo
La especificación es la única fuente de verdad sobre lo que se construye:
* Todo cambio de requisito DEBE reflejarse primero en los artefactos SDD correspondientes.
* Queda prohibido generar código de producción significativo a partir de *prompts* informales sin una especificación aprobada previa.
* Los criterios de aceptación en los Specs DEBEN ser objetivamente verificables.

### XI. Mantenibilidad, Cohesión y Ausencia de Sobreingeniería
El código DEBE guiarse por principios de simplicidad, alta cohesión, bajo acoplamiento y responsabilidad única.
* NO se introducirán patrones de diseño complejos ni abstracciones para resolver escenarios hipotéticos no requeridos (*YAGNI*).
* La deuda técnica temporal aceptada DEBE quedar explícitamente documentada en los artefactos del proyecto.

### XII. Desarrollo Enfilado, Aislamiento en Git y Trabajo Paralelo
La arquitectura y la modularidad de Specs DEBEN facilitar el trabajo simultáneo de varios desarrolladores:
* Las funcionalidades independientes DEBERÍAN desarrollarse en ramas independientes de Git (`feature/...`), especialmente cuando puedan evolucionar en paralelo.
* Los cambios DEBEN ser atómicos y los mensajes de *commit* DEBEN estar vinculados a la historia o tarea correspondiente.
* Los módulos centrales DEBEN minimizarse en puntos de fricción para evitar conflictos de integración (*merge conflicts*).

### XIII. DevOps Reproducible, Despliegue Continuo y Separación de Configuración
El proyecto DEBE poder construirse y desplegarse de manera reproducible:
* Las configuraciones específicas de entorno (desarrollo, staging, producción) DEBEN mantenerse estrictamente separadas del código fuente (vía variables de entorno).
* El flujo de integración DEBE validar en orden: Integración → Tests → Build → Deploy → Smoke Test.

### XIV. Rendimiento Pragmático y Conectividad Web
* Arus será inicialmente una aplicación web conectada. NO se implementará arquitectura *offline-first* en la primera versión.
* La aplicación DEBE gestionar fallos de conectividad de forma elegante, notificando al usuario y previniendo pérdida involuntaria de datos.
* Las operaciones pesadas (ej. generación de reportes masivos) DEBEN diseñarse de forma asíncrona o desacoplada cuando su latencia comprometa la experiencia interactiva.

### XV. Observabilidad Controlada y Registro Seguro de Errores
* Los errores devueltos al cliente DEBEN utilizar códigos HTTP estándar y mensajes amigables.
* El backend DEBE registrar logs estructurados suficientes para el diagnóstico técnico.
* Los registros de logs NUNCA DEBEN contener contraseñas, tokens, credenciales ni información confidencial.

## Technical Stack & Architecture Constraints

* **Frontend**: React.
* **Backend**: Python.
* **Persistencia**: PostgreSQL.
* **Paradigma de despliegue inicial**: Monolito Modular Web Multi-tenant.

*Decisiones Técnicas Pospuestas a Specify/Plan*:
Las siguientes decisiones NO forman parte de la Constitución y DEBEN resolverse fundadamente durante las fases de Plan y Specify:
* Selección del framework backend Python (ej. FastAPI vs Django).
* Selección de librerías UI/state management en React.
* Herramientas de ORM o acceso a base de datos.
* Mecanismos específicos de autenticación (ej. JWT, OAuth2, Session).
* Estrategia técnica detallada de RLS / esquemas en PostgreSQL.
* Proveedor de Infraestructura Cloud, Hosting y CI/CD.
* Herramientas específicas de APM / Observabilidad.

*Hitos del Demo Day*:
La arquitectura DEBE soportar la demostración de:
1. Una línea base funcional y desplegada en entorno web.
2. Al menos 10 Historias de Usuario iniciales en flujo completo (React → Python API → PostgreSQL → Response → UI).
3. Trazabilidad completa desde la especificación hasta las pruebas y el despliegue.
4. Capacidad de incorporar e integrar nuevas historias durante la demostración sin romper la estabilidad del sistema existente.

## Development Workflow & Quality Gates

El proceso de desarrollo del proyecto Arus DEBE cumplir estrictamente la secuencia Spec-Driven Development (SDD):

1. **Constitution**: Definición de gobernanza y reglas no negociables del proyecto.
2. **Specify**: Definición de especificaciones funcionales, requisitos y criterios de aceptación.
3. **Clarify**: Resolución de ambigüedades, contradicciones o lagunas cuando existan. Esta etapa se omite cuando el Spec es suficientemente claro.
4. **Plan**: Diseño técnico, decisiones de stack detalladas, contratos de API y arquitectura de datos.
5. **Tasks**: Desglose de tareas ejecutables y ordenadas por dependencia (`tasks.md`).
6. **Implementation**: Codificación y pruebas automatizadas asociadas.

*Trazabilidad Completa*:
`Necesidad → Historia → Spec → Clarify (si aplica) → Plan → Tasks → Implementation → Tests → Commit → Integración → Deploy → Validación funcional.`

## Governance

1. **Supremacía**: Esta Constitución prima sobre cualquier otra práctica, decisión de implementación o costumbre informal. En caso de conflicto entre un diseño técnico y esta Constitución, la Constitución prevalece.
2. **Procedimiento de Enmienda**: Toda enmienda a la Constitución requiere justificación formal, actualización del número de versión semántica, actualización de fechas y generación del *Sync Impact Report*.
3. **Versionado Semántico (SemVer)**:
   * **MAJOR**: Eliminación, sustitución o redefinición de principios fundamentales (cambios incompatibles de gobernanza).
   * **MINOR**: Adición de nuevos principios o secciones compatibles.
   * **PATCH**: Aclaraciones sintácticas, correcciones tipográficas o redacciones menores sin cambio de sentido.
4. **Revisión de Cumplimiento**: Todo *Pull Request* o revisión de arquitectura DEBE verificar explícitamente la conformidad con los principios definidos en este documento.

**Version**: 1.0.1 | **Ratified**: 2026-08-20 | **Last Amended**: 2026-08-20
