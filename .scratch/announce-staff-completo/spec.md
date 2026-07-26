# `/announce` completo: declarar unidad + anunciar (staff)

Fuente: `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 6 (con Grupos 1 y 4 como dependencias, ya resueltas).

## Problem Statement

Hoy `/announce` solo declara una unidad en lote (agrupa teléfonos existentes bajo un Apartamento). El staff necesita una vista más completa: poder anunciar un paquete con más datos de los que da el cliente en `/anunciar` (torre, apartamento, teléfono de notificación), y de paso declarar/actualizar la unidad y sus residentes (ahora como Ocupantes, con o sin teléfono, ver ADR-0006) en el mismo formulario — sin tener que ir a dos pantallas distintas.

Además, el staff necesita poder corregir un anuncio que quedó mal — por ejemplo, un cliente escribió "Jesu Peres" con un typo cuando el residente ya está registrado como "Jesús Pérez" (la advertencia que calcula `/paquetes`, Grupo 1, ticket 03).

## Solution

`/announce` (staff, cualquier rol) se convierte en un formulario único con tres bloques:

1. **Apartamento** (opcional en bloque: los 3 campos vacíos, o los 3 llenos) — Conjunto, Torre, Apartamento.
2. **Residentes de esa unidad** (solo si se llenó el Apartamento) — filas dinámicas Nombre + Teléfono, donde el **Teléfono ahora es opcional por fila** (a diferencia del formulario viejo, que exigía ambos). Usa la entidad Ocupante (ADR-0006): el primer residente declarado de una unidad nueva necesita teléfono (queda como Ocupante principal); los demás pueden no tenerlo. Si alguno de los residentes SÍ tiene teléfono, su Persona correspondiente también actualiza su `apartamento_actual` a esta unidad (mantiene sincronizados Ocupante y el mecanismo existente de membresía de Persona).
3. **Anunciar un paquete** (opcional — el staff puede solo declarar la unidad sin anunciar nada) — Teléfono y Nombre de quien anuncia/recibe, más un Teléfono de notificación distinto si aplica. Usa el Apartamento del bloque 1 como override del snapshot si se llenó.

Para corregir un anuncio con advertencia (Grupo 1): se agrega una acción "Corregir destinatario" accesible desde `/paquetes` para paquetes en estado `ANUNCIADO` con advertencia, que permite editar `recipient_name`/`recipient_phone` de ESE Paquete puntual. Esto es una excepción **acotada y deliberada** a la inmutabilidad de ADR-0001 — ver la nota abajo.

### Nota sobre ADR-0001 (léase antes de implementar)

ADR-0001 protege contra que el snapshot de apartamento seguido por FK **reescriba paquetes viejos automáticamente** cuando una Persona se muda — ese es el defecto que evita. Corregir un typo de nombre recién anunciado es un caso distinto: una acción **explícita, auditada, del staff**, no un efecto secundario automático de que algo más cambió. Por eso esta rebanada acota la corrección así:

- Solo aplica a Paquetes en estado **`ANUNCIADO`** (antes de que el ciclo de vida avance) — una vez `RECIBIDO`, el contexto de entrega queda tan congelado como hoy, sin excepción.
- Registra **quién** corrigió y **cuándo** (mismo patrón que las demás transiciones — actor real de la sesión, nunca hardcodeado).
- No reabre la puerta a que un cambio en Persona/Apartamento reescriba el snapshot solo — sigue siendo texto copiado, la corrección es un acto deliberado sobre ESE Paquete.

Si esta lectura de ADR-0001 no es la que se buscaba, es el punto a corregir antes de implementar el ticket de "corregir destinatario" — el resto de la rebanada (declarar unidad + anunciar) no depende de esto.

## User Stories

1. Como miembro del staff, quiero declarar Conjunto/Torre/Apartamento junto con anunciar un paquete, en un solo formulario, para no tener que ir a dos pantallas.
2. Como miembro del staff, quiero agregar residentes de una unidad sin que todos necesiten teléfono, para reconocer a quienes no tienen celular propio (Ocupante, ADR-0006).
3. Como miembro del staff, quiero que el primer residente declarado de una unidad nueva sí necesite teléfono, para que la unidad siempre tenga un contacto real.
4. Como miembro del staff, quiero anunciar un paquete con más datos que el cliente (teléfono de notificación distinto, apartamento explícito), para cubrir casos que `/anunciar` no contempla.
5. Como miembro del staff, quiero declarar solo la unidad sin anunciar ningún paquete, para poder registrar residentes de forma proactiva.
6. Como miembro del staff, quiero corregir el nombre/teléfono de un paquete recién anunciado (aún `ANUNCIADO`) cuando no coincide con lo registrado, para arreglar errores de tipeo del cliente.
7. Como miembro del staff, no quiero poder corregir el destinatario de un paquete que ya fue `RECIBIDO`, para no romper la inmutabilidad del contexto de entrega una vez el ciclo avanzó.
8. Como desarrollador, quiero que declarar residentes con teléfono también actualice el `apartamento_actual` de su Persona (no solo el registro de Ocupante), para que ambos mecanismos de membresía queden sincronizados.

## Implementation Decisions

- **Ruta `/announce`** (staff, cualquier rol — `current_staff`, no `require_admin`): reemplaza el formulario actual de declarar-unidad-en-lote.
- **Bloque Apartamento**: mismo patrón "todos vacíos o todos llenos" que ya usa `/mis-datos` para el mismo propósito.
- **Bloque Residentes**: mismo patrón de filas dinámicas del formulario viejo (+ Agregar / ×), pero el campo Teléfono deja de ser obligatorio por fila. Por cada fila con datos, se llama `agregar_ocupante(session, apartamento, nombre, telefono)`. Si el `telefono` viene y ya existe una Persona con ese teléfono, se reutiliza (comportamiento de `agregar_ocupante`, sin cambios). Además, para cada fila CON teléfono, se llama `set_apartamento_actual` sobre esa Persona con el mismo Apartamento — sincroniza el mecanismo viejo.
- **Bloque Anunciar**: usa `announce(db, telefono, nombre, Destinatario.declarado_por_cliente(nombre), apartamento=apto_del_bloque_1_o_None)`. Reutiliza el mismo modo de `Destinatario` que ya usa `/anunciar` (Grupo 1) — la diferencia staff es el resto de datos alrededor, no el modo de destinatario en sí.
- **Corregir destinatario** (nuevo, acotado a `ANUNCIADO`): nueva función de dominio `corregir_destinatario(session, paquete, actor, recipient_name, recipient_phone=None)` en `paquete_lifecycle.py` (mismo módulo que las demás transiciones) — `TransicionInvalida` si el Paquete no está `ANUNCIADO`. No cambia el `estado`; solo actualiza `recipient_name`/`recipient_phone` y dos columnas nuevas de auditoría (`corrected_at`, `corrected_by_usuario_id`). Acción nueva en `/paquetes`: junto al badge de advertencia, un botón/modal "Corregir" (mismo patrón de modal que Recibir/Entregar/Cancelar).

## Testing Decisions

- Seam de dominio (`tests/data_model/test_declarar_unidad.py`, extender): declarar con residentes con y sin teléfono; el primer residente sin teléfono de una unidad nueva falla; declarar sincroniza `apartamento_actual` de las Personas con teléfono.
- Seam de dominio nuevo (`tests/data_model/test_corregir_destinatario.py`): corregir en `ANUNCIADO` cambia `recipient_name`/`recipient_phone` y registra actor+timestamp; corregir en `RECIBIDO`/`ENTREGADO`/`CANCELADO` lanza `TransicionInvalida` sin efecto.
- Seam web (`tests/web/test_announce_new.py` o renombrado según corresponda): formulario con los 3 bloques; declarar unidad sin anunciar; anunciar con apartamento; validaciones de "todos vacíos o todos llenos"; el primer residente sin teléfono da error.
- Seam web (`tests/web/test_packages.py`): el botón/modal "Corregir" aparece solo si `ANUNCIADO` y hay advertencia; corregir exitosamente quita la advertencia (porque ahora coincide); corregir en otro estado no es posible (sin botón).

## Out of Scope

- Elegir un Ocupante existente de la unidad como destinatario desde un selector (hoy el bloque Anunciar usa teléfono+nombre libres; si el teléfono coincide con un Ocupante recién declarado, se resuelve solo vía `get_or_create_persona`, sin UI de selección explícita).
- Plantillas de notificación, LIWA — Grupo 8.
- Filtros/paginación de `/paquetes` — Grupo 5.

## Further Notes

Si la lectura de ADR-0001 en la sección "Nota" no es la esperada, avisar antes de que se implemente el ticket de "corregir destinatario" — el resto de la rebanada no depende de esa resolución y puede proceder igual.
