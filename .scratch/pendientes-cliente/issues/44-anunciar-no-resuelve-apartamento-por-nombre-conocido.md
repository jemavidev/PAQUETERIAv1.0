# 44 — `/anunciar`: paquetes quedan "Sin apartamento" cuando el teléfono que anuncia nunca fue vinculado, aunque el nombre coincida con un ocupante conocido

**Pedido original (cliente):** "No se como lo tienes contemplado, PERO con lo relacionado a los
apartamentos, la idea es que despues que una persona relacione un apartamento con el numero de
telefono del contacto principal, de hay en adelante todos los paquetes que lleguen a nombre del
contacto principal o de un ocupante del mismo sea relacionado directamente con este, no deberia
quedar 'Sin Apartamento', te digo esto por el caso de estos 2 paquetes '32TE' y '64E3'".

**Status:** formalizado — spec publicado en
`.scratch/asociacion-retroactiva-apartamento/spec.md` (`ready-for-agent`, 2026-08-04). El
seguimiento de implementación continúa allá, no en este archivo.

## Diagnóstico (vía skill `diagnosing-bugs`)

No fue posible confirmar el caso exacto de los paquetes `32TE`/`64E3` contra datos reales: el
entorno donde vive el rebuild (`test.papyrus.com.co`, host `paquetex-v2` en `~/.ssh/config`) quedó
bloqueado por el clasificador de seguridad de auto-mode al intentar conectar por SSH (host nuevo
en la sesión). Nota aparte útil: el host `staging` (`staging.jemavi.co`) al que SÍ me conecté
resultó ser la app **legacy** (`src.main:app`, base `paqueteria_staging` con tablas de
facturas/CUFE) — no tiene nada que ver con el rebuild ni con estos paquetes.

En su lugar, reproduje el mecanismo con una prueba local determinística (4 escenarios contra el
harness de tests real, borrada después de confirmar):

| Escenario | Resultado |
|---|---|
| Ocupante principal (teléfono ya vinculado) anuncia para sí mismo | ✅ resuelve el apartamento |
| Ocupante NO-principal, pero con SU PROPIO teléfono ya registrado, anuncia para sí mismo | ✅ resuelve el apartamento (esto ya funciona hoy) |
| Principal anuncia a nombre de un familiar sin teléfono que YA está en el roster de Ocupantes de su unidad | ✅ resuelve el apartamento |
| **Un teléfono NUEVO (nunca visto, nunca vinculado a ningún apartamento) anuncia declarando el NOMBRE EXACTO de un Ocupante conocido de otro teléfono** | ❌ **"Sin apartamento"** |

**Causa raíz:** `paquete_service.announce()` resuelve el apartamento leyendo
`persona_destino.apartamento_actual_id` (o el del Anunciante si no hay destinatario con Persona
propia) — nunca busca por NOMBRE fuera de ese caso. El único lugar que compara el nombre
declarado contra un roster (`_resolver_ocupante_por_nombre`) exige que el ANUNCIANTE ya sea
Ocupante activo de algún apartamento, y solo busca coincidencias DENTRO de esa misma unidad — no
busca en todo el edificio. Es decir: la resolución automática hoy depende 100% de que el TELÉFONO
que anuncia ya esté vinculado (como principal u ocupante) — nunca del nombre por sí solo. Esto es
además una decisión ya documentada explícitamente en el código
(`apartamento_service.declare_unit`): *"Un 'a nombre de' casual en `announce` NO pasa por aquí y
por tanto NO agrupa a nadie."*

Hipótesis más probable para `32TE`/`64E3` (pendiente de confirmar contra datos reales): se
anunciaron desde un teléfono que nunca pasó por `/mis-datos` ni fue agregado como Ocupante de ese
apartamento — aunque el NOMBRE escrito coincidiera con el contacto principal real.

## Opciones para resolverlo (requieren tu decisión — hay un trade-off real de seguridad/privacidad)

**Opción A — Buscar por nombre en TODO el edificio cuando el teléfono es nuevo.** Si el nombre
declarado coincide EXACTO con un único Ocupante activo en cualquier apartamento del sistema, se
resuelve automático a esa unidad. Riesgo real: dos personas con el mismo nombre en apartamentos
distintos (nombres comunes) podrían hacer que un paquete se asocie al apartamento equivocado —
mitigable exigiendo coincidencia única (si hay más de un "Juan Pérez" en el edificio, no se
resuelve automático, sigue "Sin apartamento" como hoy).

**Opción B — No tocar la resolución automática; mejorar la corrección manual.** Ya existe
`paquete_correccion_service.py` y el propio `/anunciar` documenta que "el staff lo verá señalado
en `/paquetes` y lo resuelve desde `/announce`" cuando el nombre no coincide. Más seguro, pero no
resuelve lo que pediste (que quede vinculado automáticamente).

**Opción C — Híbrido:** la resolución automática sigue siendo solo por teléfono (sin riesgo de
colisión), pero cuando el nombre declarado coincide con un Ocupante conocido, se le muestra al
staff como sugerencia destacada en la pantalla de corrección (un clic en vez de buscar a mano) en
vez de auto-asignar.

Necesito que elijas antes de tocar código — es lógica de dominio con implicación real de a quién
se le muestra la info de un paquete, no un ajuste de estilo.

## Diseño acordado con el cliente (2026-08-04)

El cliente aclaró el mecanismo completo, distinto a las 3 opciones originales — es una variante de
la Opción C con autorización explícita del staff en vez de solo búsqueda por nombre:

1. **La resolución automática por teléfono ya vinculado sigue exactamente igual** (nunca se busca
   por nombre en todo el edificio — se descarta la Opción A por el riesgo de colisión de nombres).
2. **Nuevo:** cuando un teléfono se vincula por primera vez a un apartamento (como principal vía
   `agregar_ocupante`/primer ocupante, o como ocupante secundario vía `agregar_ocupante`/
   `asociar_telefono_a_ocupante`), el sistema debe detectar si ese teléfono ya tiene Paquetes
   anunciados bajo él (`announced_by_phone` o `recipient_phone`) SIN apartamento
   (`snapshot_apartamento IS NULL`) — "paquetes huérfanos".
3. **Elegibilidad para re-asociación retroactiva — SOLO `estado == ANUNCIADO`.** Recibido,
   Entregado y Cancelado quedan congelados para siempre (confirma/extiende ADR-0001: el snapshot
   solo es corregible retroactivamente mientras el paquete no ha sido recibido físicamente; una vez
   recibido, entregado o cancelado, nunca se toca).
4. **Cuándo se autoriza — depende de quién hace la inscripción:**
   - **Si es el STAFF quien inscribe el teléfono** (en persona, ej. vía `/announce` o el panel de
     administración): la re-asociación de huérfanos ANUNCIADO se aplica EN EL MISMO PASO, sin
     aviso ni confirmación aparte — el staff ya está presente y decidiendo.
   - **Si es autoservicio** (residente vía `/mis-datos`, inscribiéndose a sí mismo o a un ocupante
     secundario): la inscripción del ocupante/teléfono en sí NO se bloquea ni se detiene (el
     residente la ve aplicada de inmediato, como hoy). Pero la re-asociación de paquetes huérfanos
     NO es automática en este caso — le aparece al staff un aviso puntual para que la autorice
     explícitamente.
5. **Ubicación del aviso — puntual, no una cola/panel centralizado aparte** (se descartó
   explícitamente una bandeja de pendientes separada). Falta definir la pantalla staff exacta
   donde aparece para el caso de autoservicio (el cliente no lo especificó) — propuesta pendiente
   de confirmar: mostrarlo como aviso contextual en la ficha del apartamento/cliente
   (`customers_manage/detail.html`) la próxima vez que el staff la abra, en vez de crear una
   pantalla nueva dedicada.

## Alcance real de este cambio

Toca: `paquete_service.py` (nueva consulta de huérfanos), `ocupante_service.py` +
`apartamento_service.py` (disparar la detección al vincular un teléfono), posiblemente
`paquete_correccion_service.py` (la re-asociación en sí es una escritura de snapshot, algo que
hoy ADR-0001 declara inmutable — hay que decidir si se modela como una excepción documentada a esa
regla o como un nuevo evento de dominio), y una superficie de UI staff nueva (el aviso). Es un
cambio de dominio real con una modificación de una invariante ya documentada (ADR-0001) — candidato
claro para `/to-spec` → `/to-tickets` en vez de resolverse ad-hoc en este hilo de pedidos puntuales.

## Comments
