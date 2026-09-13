Status: ready-for-agent
Feature: dinero-contra-entrega-control
Branch: PaqueteXv.2
Fuente de verdad: sesión de `/grilling` con el cliente (esta conversación) · `.scratch/dinero-contra-entrega/spec.md` (módulo original, ya implementado — esta es una extensión de solo lectura sobre esa misma entidad)

---

## Problem Statement

El módulo de dinero contra entrega (`.scratch/dinero-contra-entrega`) ya registra cada depósito, pago
a mensajero y recuperación como un movimiento propio (`MovimientoSaldoContraEntrega`), y ya muestra a
cualquier miembro del staff qué residentes tienen saldo distinto de cero (`/residentes/saldos-contra-
entrega`). Pero ese listado es solo una foto del saldo actual — no muestra NINGÚN movimiento
individual. Hoy, si el cliente quiere saber cuánto se registró a favor o en contra de un residente
puntual, en qué fecha y hora, quién de staff lo registró, si fue un ingreso o un egreso, y a qué
paquete se le aplicó, no hay ningún lugar del sistema (para staff) donde consultar eso — el dato ya
existe en la base de datos (la entidad es append-only, nunca se edita ni se borra), pero nadie puede
verlo. El cliente necesita poder hacer seguimiento a este dinero.

## Solution

Dos vistas nuevas, ambas de solo lectura sobre `MovimientoSaldoContraEntrega` (ninguna escritura
nueva, ninguna columna nueva):

1. **Un ledger global**, en una ruta nueva bajo `/residentes`, enlazada desde la página de resumen
   actual (`/residentes/saldos-contra-entrega`) con un link "Ver historial completo". Lista TODOS los
   movimientos de TODOS los residentes, más recientes primero, con filtro por residente (nombre,
   teléfono o usuario de WhatsApp) y por tipo (ingreso vs. egreso, según el signo de `monto`).
   Accesible a cualquier rol de staff — mismo criterio que el resto de este módulo, no exclusivo de
   Admin.
2. **Un historial por residente**, agregado dentro del modal "Saldo" que ya existe en la ficha de
   cada residente (`/residentes/{id}`) — debajo del saldo actual y del formulario de "Actualizar" que
   ya están ahí, se agrega la lista de movimientos de esa Persona.

Cada movimiento se muestra con: monto (con signo, ingreso en verde / egreso en rojo, mismo criterio
visual que la píldora "Saldo" ya existente), fecha y hora, quién de staff lo registró, y el paquete al
que se aplicó (si tiene uno — un link al código de acceso del paquete) o una indicación de que fue un
movimiento manual sin paquete asociado.

## User Stories

1. Como miembro del staff, quiero ver una lista cronológica de TODOS los movimientos de saldo contra
   entrega del conjunto, para poder hacer seguimiento/auditoría del dinero sin tener que revisar
   residente por residente.
2. Como miembro del staff, quiero filtrar ese ledger por residente (nombre, teléfono o WhatsApp), para
   encontrar rápido los movimientos de una persona puntual.
3. Como miembro del staff, quiero filtrar ese ledger por ingreso o egreso, para separar depósitos/
   recuperaciones de pagos a mensajeros/vueltas entregadas.
4. Como miembro del staff, quiero ver de cada movimiento: el monto exacto, la fecha, la hora, quién de
   staff lo registró, y si fue un ingreso o un egreso — sin tener que inferirlo del signo del número.
5. Como miembro del staff, quiero ver a qué paquete se aplicó cada movimiento (si aplica), con un link
   directo a ese paquete, para poder cruzar la información sin buscar el código a mano.
6. Como miembro del staff, quiero que un movimiento sin paquete asociado (depósito o recuperación
   manual) se distinga claramente de uno que sí tiene paquete, en vez de mostrar un campo vacío.
7. Como miembro del staff (cualquier rol, no solo Admin), quiero poder acceder a este ledger global —
   es una herramienta operativa del día a día, mismo criterio de permisos que el resto del módulo.
8. Como miembro del staff, desde la página de resumen de saldos (`/residentes/saldos-contra-entrega`),
   quiero un link directo hacia el ledger completo, para no tener que recordar o teclear otra URL.
9. Como miembro del staff, en la ficha de un residente puntual, quiero ver su historial de movimientos
   directamente en el modal "Saldo" que ya uso para consultar su saldo actual y registrar uno nuevo,
   en vez de tener que ir al ledger global y filtrar por su nombre.
10. Como miembro del staff, si un residente nunca tuvo ningún movimiento, quiero que el historial de
    su modal "Saldo" lo diga claramente (una lista vacía con un mensaje), no un error ni una sección
    rota.
11. Como sistema, quiero que ninguna de estas dos vistas permita editar ni borrar un movimiento — son
    puramente de lectura, el criterio de append-only del módulo original no cambia.
12. Como sistema, quiero que el ledger global pagine igual que el resto de listados largos del sistema
    (`/residentes`, `/paquetes`), para no cargar todo el historial del conjunto en una sola respuesta.

## Implementation Decisions

- **Nueva función de dominio** en `saldo_contra_entrega_service.py` — lista movimientos de TODAS las
  Personas (no de una sola, a diferencia de `movimientos_de_persona` ya existente), más recientes
  primero, con filtro opcional por término de búsqueda (nombre/teléfono/WhatsApp de la Persona
  asociada) y por signo del monto (ingreso: `monto > 0`, egreso: `monto < 0`). Devuelve la Persona y
  el Usuario de staff ya resueltos (batch, mismo criterio "un puñado fijo de consultas" que
  `packages.py::_listar`), no uno por fila. Paginada (mismo patrón `_POR_PAGINA`/offset-limit que
  `_listar_todos_los_residentes` en `customers_manage.py`).
- **Nueva ruta `GET /residentes/movimientos-saldo-contra-entrega`** (`customers_manage.py`, mismo
  router y mismo criterio de permisos que `/residentes/saldos-contra-entrega` — `current_staff`,
  cualquier rol). Registrada como ruta ESTÁTICA antes de `/residentes/{persona_id}` (mismo cuidado de
  orden de registro que ya tiene la ruta de resumen — ver su propio comentario en el código). Acepta
  `q` (término de búsqueda por residente) y un parámetro de tipo (`ingreso`/`egreso`/vacío = ambos) +
  `pagina`.
- **Extensión de la plantilla de resumen** (`saldos_contra_entrega.html`): agrega un link "Ver
  historial completo" hacia la nueva ruta.
- **Nueva plantilla** para el ledger — tabla con columnas Residente / Monto (con color) / Fecha y hora
  / Registrado por / Paquete (link al código de acceso, o "Movimiento manual" si `paquete_id` es
  nulo), filtros de búsqueda y tipo en la parte superior (mismo patrón visual que
  `saldos_contra_entrega.html`/`_busqueda_filtros.html`), paginación al pie (mismo componente que
  `/residentes`).
- **Extensión del modal "Saldo"** (`customers_manage/detail.html`, dentro de `{% call modal('saldo',
  'Saldo') %}`): debajo del formulario de "Actualizar" ya existente, agrega la lista de movimientos de
  esa Persona (reusa `movimientos_de_persona`, ya existente — la misma función que hoy solo consume
  `/mis-datos`). Mismo formato de fila que el ledger global, sin la columna Residente (ya se sabe de
  quién es la ficha) y sin filtros (es un historial acotado a una sola persona).
- **Sin cambios en el modelo de datos** — `MovimientoSaldoContraEntrega` ya tiene todas las columnas
  necesarias (`monto`, `paquete_id`, `registrado_por_usuario_id`, `created_at`); ninguna migración
  nueva.
- **Sin cambios en `registrar_movimiento_saldo`** ni en ningún flujo de escritura existente (Recibir,
  Entregar, depósito/recuperación standalone) — esto es puramente una capa de lectura nueva encima de
  datos que el módulo original ya escribe.

## Testing Decisions

Buen test acá = observar comportamiento externo (qué devuelve la función nueva, qué HTML/status se
renderiza) — nunca aserciones sobre el código interno. Mismo criterio que el resto del módulo
(`.scratch/dinero-contra-entrega/spec.md`, sección Testing Decisions).

- **Seam 1 — la función de dominio nueva** (extensión de `tests/data_model/test_saldo_contra_entrega_
  service.py`, ya existente del módulo original): devuelve movimientos de VARIAS Personas distintas
  mezclados y ordenados por fecha descendente; el filtro por término de búsqueda encuentra por
  nombre/teléfono/WhatsApp; el filtro de ingreso/egreso separa correctamente por signo de `monto`; la
  paginación corta en el tamaño esperado.
- **Seam 2 — la ruta del ledger global** (extensión de `tests/web/test_customers_manage.py`, prior
  art: los tests ya existentes de `/residentes/saldos-contra-entrega`): accesible a cualquier rol de
  staff (no solo Admin); sin filtros, lista todos los movimientos recientes; con `q`, filtra por
  residente; con el filtro de tipo, separa ingresos de egresos; un movimiento con `paquete_id` muestra
  un link al código de acceso de ese paquete; uno sin `paquete_id` se distingue claramente.
- **Seam 3 — el modal "Saldo" ampliado** (extensión de los tests ya existentes de esa ficha): una
  Persona con movimientos los ve listados en su propio modal; una Persona sin ningún movimiento ve un
  mensaje de lista vacía, no un error.

## Out of Scope

- Cualquier forma de editar o borrar un movimiento desde estas vistas — siguen siendo, como el resto
  del módulo, estrictamente append-only.
- Exportar el ledger (CSV/Excel/PDF) — puramente una vista en pantalla por ahora.
- Filtro por rango de fechas, por quién lo registró (staff), o por torre/apartamento — se
  descartaron explícitamente en el grilling de esta conversación; si hacen falta después, son una
  extensión aparte.
- Cualquier cambio a `registrar_movimiento_saldo` o a los flujos de Recibir/Entregar/depósito
  standalone que ya escriben movimientos — esta spec es puramente de lectura.
- Página o vista exclusiva de Admin — se descartó explícitamente; el criterio de permisos es el mismo
  del resto del módulo (cualquier staff).

## Further Notes

- Esta spec depende enteramente de la entidad y las funciones que ya construyó
  `.scratch/dinero-contra-entrega` (módulo original, ya implementado) — no crea ninguna entidad ni
  función de escritura nueva, solo lectura/presentación sobre datos que ya existen completos.
- El bug de identidad-por-nombre encontrado y corregido en esta misma conversación (`packages.py::_
  personas_por_nombre`/`_resolver_persona_destino`, exclusión de `Persona.desvinculada_en`) es
  relevante como antecedente de diseño, pero NO aplica a esta spec: acá cada movimiento ya tiene su
  propio `persona_id` real (FK directa, nunca se resuelve por nombre), así que no hay ninguna
  ambigüedad de identidad que resolver.
