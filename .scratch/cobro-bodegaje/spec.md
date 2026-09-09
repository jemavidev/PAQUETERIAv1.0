Status: ready-for-agent
Feature: cobro-bodegaje
Branch: PaqueteXv.2
Fuente de verdad: sesión de `/grilling` con el cliente (esta conversación, módulo 1 de 5) · issue 331
(`.scratch/pendientes-cliente`, bandera "primera entrega a este cliente", se reutiliza) ·
CONTEXT.md (glosario)

---

## Problem Statement

Hoy no existe ningún registro de dinero en el sistema activo (`domain`/`web`) — el staff cobra en
efectivo por la recepción de un paquete (paquete normal, caja/extra-dimensionado, y bodegaje por
días de más en portería) pero nada de eso queda anotado en ningún lado. El cliente necesita saber
cuánto se recauda por este servicio, con estadísticas por día/mes/año y por cliente/apartamento, y
necesita que el monto exacto de cada cobro quede como un registro histórico inmutable — hoy
simplemente no hay forma de responder "¿cuánto cobramos el mes pasado?" ni "¿cuánto se le cobró a
este paquete puntual?".

## Solution

Al momento de **Entregar** un paquete (`Recibido → Entregado`, único endpoint que ya existe hoy,
compartido por la vista de staff y la de `/consultar`), el sistema calcula automáticamente el monto
a cobrar y lo registra en la misma operación que marca el paquete como entregado — sin que el staff
tenga que decidir nada más allá de confirmar o anular.

El monto tiene hasta dos componentes:
- **Cargo base**, según el `TipoPaquete` ya capturado al Recibir (Normal o Extra-dimensionado/caja)
  — valor fijo configurable. Se **exime por completo** si ese paquete es "primera entrega a este
  cliente" (bandera ya existente, por teléfono del destinatario).
- **Cargo de bodegaje**, si pasaron más de 48 horas desde que se Recibió el paquete — un bloque de
  cobro por cada 24 horas iniciadas a partir de ese punto, con una tarifa propia por tipo de
  paquete. **Nunca se exime**, ni siquiera en la primera entrega a un cliente nuevo.

El staff puede anular el cobro completo a **"$0 pesos"** (ambos componentes a la vez, no por
separado) eligiendo un motivo de un catálogo cerrado y administrable (mismo patrón que ya existe
para los motivos de cancelación de un paquete). Una vez registrado — cobrado o anulado — el
registro es **inmutable para siempre**: no existe ninguna forma de corregirlo después, ni para
admin.

Las 4 tarifas (cargo base Normal/Extra-dimensionado, bodegaje/24h Normal/Extra-dimensionado) son
valores fijos editables por un admin — no un catálogo abierto donde se puedan agregar tipos de
cobro nuevos. Cada registro de cobro guarda el monto real aplicado en ese momento, así que cambiar
una tarifa a futuro nunca altera un cobro ya hecho.

El monto cobrado (o "$0" + motivo) se muestra en el detalle/timeline del paquete, visible para
cualquier miembro del staff. Además, una página nueva de solo lectura bajo `/administracion`
(exclusiva de admin) muestra estadísticas agregadas — cantidad y monto por rango de fechas
(día/mes/año), desglose por cliente/apartamento, tiempo promedio de bodegaje — sin exportar a
archivo ni filtros avanzados en esta primera versión.

No se captura el medio de pago (efectivo, transferencia, etc.) — solo que se cobró (o no) y cuánto.
La notificación de entrega al residente no cambia; no menciona el cobro.

## User Stories

1. Como miembro del staff, al entregar un paquete Normal que nunca fue primera entrega a ese
   teléfono ni superó las 48 horas de bodegaje, quiero que el sistema me muestre un cargo de $1.500
   ya calculado, para no tener que decidir el monto yo mismo.
2. Como miembro del staff, al entregar una caja (Extra-dimensionado) en las mismas condiciones,
   quiero que el cargo calculado sea $2.000, respetando la tarifa propia de ese tipo.
3. Como miembro del staff, al entregar un paquete que es la primera entrega histórica a ese
   teléfono, quiero que el cargo base se exima automáticamente (quede en $0), sin tener que
   marcarlo yo.
4. Como miembro del staff, si ese mismo paquete de primera entrega también superó las 48 horas en
   portería, quiero que el bodegaje se siga cobrando igual, porque la exención de primera entrega
   es solo sobre el cargo base.
5. Como sistema, quiero calcular el bodegaje como un bloque de cobro por cada 24 horas iniciadas a
   partir del minuto 48:01 desde que el paquete fue Recibido (ej. 50 horas transcurridas = 1
   bloque; 73 horas = 2 bloques), para que el cobro refleje exactamente cuánto tiempo estuvo
   guardado.
6. Como miembro del staff, quiero poder anular el cobro completo a "$0 pesos" cuando corresponda
   (ej. una novedad, un reclamo), en vez de forzar el cobro calculado.
7. Como miembro del staff, al anular a "$0", quiero que el sistema me exija elegir un motivo de una
   lista predefinida, para que quede un registro de por qué no se cobró.
8. Como admin, quiero poder crear y eliminar motivos de esa lista (sin un campo "activo", borrado
   directo), con el mismo patrón que ya uso para los motivos de cancelación de un paquete.
9. Como miembro del staff, quiero que registrar el cobro (calculado o anulado) sea parte de la
   MISMA acción de Entregar — un solo formulario, un solo submit — para no poder entregar sin
   dejar el cobro resuelto, y para no arriesgarme a cobrar dos veces si alguien reintenta.
10. Como sistema, una vez que un paquete queda Entregado con su cobro registrado, quiero que ese
    registro sea inmutable para siempre — ninguna ruta, ni de admin, permite editarlo o borrarlo
    después.
11. Como admin, quiero poder editar las 4 tarifas fijas (cargo base Normal, cargo base
    Extra-dimensionado, bodegaje/24h Normal, bodegaje/24h Extra-dimensionado) desde una pantalla de
    configuración simple, sin poder agregar un quinto tipo de cobro ni eliminar ninguno de los 4.
12. Como sistema, quiero que cada cobro guarde el monto realmente aplicado en el momento (no una
    referencia viva a la tarifa configurada), para que cambiar una tarifa a futuro nunca reescriba
    un cobro histórico.
13. Como miembro del staff, quiero ver el monto cobrado (o "$0" + motivo) en el detalle/timeline de
    un paquete ya entregado, para poder verificar de un vistazo si se le cobró y cuánto, sin ser
    admin.
14. Como admin, quiero una página de estadísticas agregadas bajo `/administracion` con un selector
    de rango de fechas (día/mes/año), para saber cuánto se recaudó y cuántos paquetes se cobraron
    en un período dado.
15. Como admin, en esa misma página, quiero ver el desglose por cliente/apartamento y el tiempo
    promedio de bodegaje, para entender patrones de uso además del total recaudado.
16. Como admin, NO necesito exportar estas estadísticas a un archivo ni filtrarlas de formas más
    finas en esta primera versión — alcanza con el selector de rango de fechas.
17. Como sistema, NO capturo el medio de pago (efectivo, transferencia, etc.) de un cobro — solo el
    monto y si se cobró o se anuló.
18. Como residente, NO quiero que la notificación de entrega de mi paquete mencione ningún monto
    cobrado — el cobro queda como información puramente interna del staff/admin.
19. Como miembro del staff, quiero que el flujo de cobro funcione igual en las dos vistas donde hoy
    existe el modal Entregar (`/paquetes` y `/consultar`), ya que ambas llaman al mismo endpoint,
    para no tener que mantener dos implementaciones distintas.
20. Como sistema, si un paquete llega a Cancelado en vez de Entregado, NO quiero generar ningún
    registro de cobro para él — el cobro solo existe atado a una entrega real.

## Implementation Decisions

- **Nueva entidad `Cobro`** (`src/app/domain/`), relación 1↔1 con `Paquete` (existe únicamente si el
  paquete llegó a `Entregado`). Campos: `paquete_id` (FK, único), `monto_base`, `bloques_bodegaje`,
  `monto_bodegaje`, `monto_total` (puede ser 0 si se anuló), `motivo_anulacion_id` (FK nullable,
  solo si `monto_total = 0` por anulación explícita, nunca porque el cálculo dio 0 por primera
  entrega — distinguir ambos casos en el dato, no inferirlo del monto), `cobrado_por_usuario_id`,
  `cobrado_en` (mismo instante que `delivered_at`). Sin `updated_at` — no hay updates posteriores
  posibles.
- **Nueva función pura `calcular_cobro(paquete, tarifas, ahora) -> DesgloseCobro`** en
  `paquete_service.py` — recibe el `Paquete` (con su `package_type`/`received_at`/`recipient_phone`
  ya resueltos), las tarifas vigentes, y el instante actual; devuelve el desglose (cargo base,
  bloques de bodegaje, monto de bodegaje, total) sin tocar la base de datos. Internamente reusa
  `es_primera_entrega_a_telefono` (ya existe) para la exención del cargo base. Fórmula de bodegaje:
  `bloques = ceil((horas_transcurridas - 48) / 24)` si `horas_transcurridas > 48`, si no `0`.
- **Nueva entidad `TarifaCobro`** (fila única de configuración, mismo patrón singleton que
  `ConfiguracionConjunto`) con las 4 tarifas como columnas nombradas (no un catálogo de filas). Sin
  historial de versiones — el valor vigente es el único que se lee al calcular; la inmutabilidad
  histórica la garantiza `Cobro.monto_base`/`monto_bodegaje` (snapshot), no la tarifa.
- **Nueva entidad `MotivoAnulacionCobro`** (`id`, `etiqueta` única, sin campo `activo`, borrado
  directo) — mismo molde exacto que `MotivoCancelacion`.
- **Extensión del endpoint único `POST /paquetes/{id}/entregar`** (`packages.py`, ya compartido por
  `_resultados.html` y `search/form.html`): acepta el monto ya calculado (recalculado server-side,
  nunca confiado del cliente) más, opcionalmente, `motivo_anulacion_id` si el staff marcó "$0". En
  una sola transacción: llama a `deliver()` (sin cambios en su firma actual) y crea el `Cobro`
  correspondiente. Si algo falla, ninguna de las dos partes queda aplicada.
- **Modal Entregar** (`components` compartidos entre ambos templates): agrega el desglose calculado
  (cargo base + bodegaje si aplica, total) y un control "$0 pesos" que revela un selector del
  catálogo de motivos (obligatorio para poder confirmar la anulación).
- **Rutas nuevas de admin** (`admin.py`, mismo patrón que `/administracion/notificaciones/motivos` y
  `/administracion/conjunto`):
  - `/administracion/tarifas-cobro` (GET/POST) — edita las 4 tarifas de `TarifaCobro`, exclusivo de
    `require_admin`.
  - `/administracion/motivos-anulacion-cobro` (crear/eliminar) — exclusivo de `require_admin`.
  - `/administracion/estadisticas-cobro` (GET, solo lectura) — agregados por rango de fechas
    (día/mes/año), desglose por cliente/apartamento (agrupando por los campos snapshot
    `snapshot_torre`/`snapshot_apartamento`/`recipient_phone`, mismo patrón usado hoy para
    agregaciones sin N+1 en `customers_manage.py`), tiempo promedio de bodegaje. Exclusivo de
    `require_admin`.
- **Detalle/timeline del paquete** (`paquete_timeline_service.py` o el template que renderiza el
  detalle de un paquete `Entregado`): muestra el `Cobro` asociado (monto o "$0" + motivo de
  `MotivoAnulacionCobro`), visible para cualquier `current_staff`.
- **Sin cambios** en `deliver()` (`paquete_lifecycle.py`), en la notificación de entrega
  (`notificacion_service.py`), ni en el modelo `Paquete` — el cobro vive enteramente en la entidad
  nueva `Cobro`, atado por FK.

## Testing Decisions

Buen test acá = observar comportamiento externo (qué devuelve la ruta HTTP, qué queda en la fila de
`Cobro`/`Paquete` después, qué HTML se renderiza) — nunca aserciones sobre el código interno.

- **Seam 1 — `calcular_cobro` (cálculo puro)**: prior art de estilo, `tests/data_model/` (ej.
  `test_motivo_cancelacion.py`, `test_configuracion_conjunto_service.py` para servicios de dominio
  chicos y puros). Cubrir: cargo base por cada `TipoPaquete`; exención de base en primera entrega;
  bodegaje NO exento en primera entrega; fórmula de bloques (0 bloques a las 48h exactas, 1 bloque a
  las 48h01, 1 bloque a las 71h59, 2 bloques a las 72h01); tarifas de bodegaje distintas por tipo.
- **Seam 2 — `POST /paquetes/{id}/entregar` con cobro** (`tests/web/test_packages.py`, prior art
  directo: `test_entregar_un_recibido_transiciona_y_registra_al_actor`,
  `test_entregar_un_no_recibido_se_rechaza_sin_efecto`): entregar crea el `Cobro` con el monto
  calculado; entregar con "$0" exige y guarda el `motivo_anulacion_id`; entregar sin resolver el
  cobro (ej. eligió "$0" sin motivo) se rechaza sin transicionar el paquete ni crear el `Cobro`;
  el mismo flujo funciona igual llamado desde el contexto de `/consultar` que desde `/paquetes`.
- **Seam 3 — inmutabilidad**: no existe ninguna ruta que edite/borre un `Cobro` — cubrir con un test
  que confirme que no hay endpoint expuesto para eso (ausencia de ruta, no un test de rechazo en
  runtime).
- **Seam 4 — rutas de admin** (`tests/web/test_admin_conjunto.py`,
  `tests/web/test_admin_notificaciones.py` como prior art directo de estilo): editar tarifas
  (exclusivo admin, un operador recibe 403); crear/eliminar motivo de anulación (exclusivo admin);
  estadísticas devuelven los totales esperados para un rango de fechas armado a propósito en el
  test (paquetes con cobro y con "$0" mezclados).
- **Seam 5 — detalle/timeline**: el monto o "$0"+motivo aparece en el HTML del detalle de un
  paquete `Entregado`; no aparece nada de esto para un paquete `Anunciado`/`Recibido`/`Cancelado`
  (no tiene `Cobro`).

## Out of Scope

- Cualquier procesamiento real de pago (pasarela de tarjeta, PSE, etc.) — es solo registro de un
  cobro ya hecho en efectivo/otro medio fuera del sistema.
- Captura del medio de pago (efectivo, transferencia, etc.).
- Corrección o ajuste de un `Cobro` después de creado, por cualquier rol.
- Catálogo abierto de tipos de cobro — las 4 tarifas son fijas, no se pueden agregar ni quitar.
- Exportar las estadísticas a CSV/Excel, o cualquier filtro más allá del rango de fechas.
- Cambios a la notificación de entrega (WhatsApp/SMS) para mencionar el cobro.
- Historial de versiones de las tarifas (solo se guarda el valor vigente; la historia la preserva
  cada `Cobro` por snapshot).

## Further Notes

- Este spec es el primero de 5 módulos diseñados en la misma sesión de `/grilling` con el cliente
  (los otros 4: consolidación de contactos, migración por año de `access_code`, bloquear clientes,
  y dinero contra entrega) — se publican como specs independientes, uno por módulo.
- La bandera "primera entrega a este cliente" (`es_primera_entrega_a_telefono`,
  `paquete_service.py`) ya existe y no cambia de criterio (sigue siendo por teléfono del
  destinatario) — este módulo solo la consume para la exención del cargo base.
