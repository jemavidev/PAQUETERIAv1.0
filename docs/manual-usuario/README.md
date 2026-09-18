# Manual de usuario — mapa de features por audiencia

Punto de partida para documentar PaqueteXv.2 de cara al usuario final. Antes de
escribir contenido de ayuda hay que tener claro **qué existe y para quién** —
este directorio fija ese inventario, derivado de inspeccionar rutas
(`CODE/src/app/web/routes/`), plantillas (`CODE/src/app/web/templates/`) y las
puertas de acceso (`CODE/src/app/web/security.py`) del sistema en su estado
actual (2026-09-18).

El dominio real solo reconoce dos audiencias (`CONTEXT.md`, sección "Las dos
audiencias"): **Staff** (`Usuario`, roles `ADMIN`/`OPERADOR`) y **Cliente**
(`Persona`, residente, sin privilegios). Para efectos de manual de usuario
final conviene partirlo en 3, porque son 3 públicos con necesidades de
documentación distintas:

1. [Vista pública](01-vista-publica.md) — visitantes anónimos y residentes
   logueados (`current_customer`). Nunca staff.
2. [Vista staff operador](02-staff-operador.md) — cualquier `Usuario` con
   sesión (`current_staff`), rol `OPERADOR` o `ADMIN`.
3. [Vista staff admin](03-staff-admin.md) — superset del operador, todo lo
   detrás de `require_admin`.

## Cómo se armó este inventario

Por cada módulo de rutas se identificó qué dependencia de FastAPI protege
cada endpoint (`current_staff`, `require_admin`, `current_customer`, o
ninguna), y se cruzó con las plantillas y el menú real (`base.html`, bloques
`bloque_cliente()` / `bloque_staff()`) para confirmar cómo se agrupa en la
navegación que el usuario final efectivamente ve.

## Estado — no confundir con el manual final

Los tres documentos ya se reescribieron como guía de uso completa, con
tono directo al lector (paso a paso, ejemplos concretos con el mismo caso
ficticio compartido entre los tres) — pensados para que los lea
directamente un residente, un Operador o un Admin, no como documentación
técnica. Sirven además de insumo para reescribir `/ayuda`, `/terminos`,
`/privacidad`, `/cookies` (contenido público — ver hallazgo abajo).

### Pendiente de seguimiento (para quien mantiene este directorio, no para
quien lee las guías)

- **Capturas de pantalla reales** en los tres documentos — hoy todo está
  descrito en texto, sin un solo ejemplo visual.
- **Validarlos con usuarios reales** — un residente para 01, staff para 02
  y 03 — confirmar que el orden de los bloques coincide con cómo se usa de
  verdad, y detectar qué falta explicar mejor.
- **Una sección de errores frecuentes**, aparte de las reglas ya explicadas
  dentro de cada bloque.
- **El typo "Servecio normal"/"Servidio Extra-dimensionado"** en
  Administración → Tarifas de cobro (documentado tal cual en 03, sección
  Cobros) — confirmar con el cliente si era la intención real del pedido o
  se coló un error de tipeo al aplicarlo (commit `baa0d0d`).
- Fuente de 01: `CODE/src/app/web/routes/announce.py`, `search.py`,
  `entrar.py`, `customer_auth.py`, `customer_paquetes.py`,
  `customer_verify.py`, `password_reset.py`, `ayuda.py`, `terms.py`,
  `privacy.py`, `cookies.py`.
- Fuente de 02 y 03: `CODE/src/app/web/routes/packages.py`,
  `customers_manage.py`, `announce_new.py`, `auth.py`, `admin.py`,
  `admin_proveedores.py`, y sus plantillas en
  `CODE/src/app/web/templates/{packages,customers_manage,components,admin}/`.
- Decidir si esto termina viviendo tal cual en el repo (`docs/`) o se migra
  a una herramienta de documentación de cara al cliente/staff final (fuera
  del alcance de este repo).

**Hallazgo relevante:** las 4 páginas legales/informativas actuales
(`/ayuda`, `/terminos`, `/privacidad`, `/cookies`) son una "réplica idéntica"
(comentario literal en las plantillas) del sitio de producción **anterior**
(`paquetex.papyrus.com.co`, Noviembre 2025) — tarifas fijas ($1.500/$2.000/
$1.000 por día), horarios y FAQ que no reflejan el modelo de dominio actual
del rebuild (Ocupante, Apartamento, OTP, saldo contra entrega, tarifas
configurables en `/administracion/tarifas-cobro`, proveedores de notificación
configurables en `/administracion/proveedores`). Antes de reescribirlas hace
falta resolver qué es vigente y qué no — ver conversación en curso.
