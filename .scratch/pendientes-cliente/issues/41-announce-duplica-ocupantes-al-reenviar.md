# 41 — `/announce` (staff) duplica Ocupantes si se reenvía el mismo residente

**Origen:** encontrado durante una prueba E2E analítica pedida por el
cliente ("necesito que analiticamente pruebes TODO lo que este disponible
en el app"), no un pedido de cambio de comportamiento — es un bug real.

**Status:** verificado

## Diagnóstico

`announce_new.py` (`POST /announce`, formulario de staff "declarar unidad +
anunciar") llama `agregar_ocupante(db, apto, nombre, telefono)` para cada
fila de "Residentes", sin chequear primero si esa Persona (o ese nombre, si
no tiene teléfono) ya es un Ocupante ACTIVO de esa misma unidad.
`agregar_ocupante` sí valida "no ser Ocupante activo de OTRO apartamento",
pero no protege contra crear un duplicado en el MISMO apartamento.

Reproducido limpio: 3 envíos idénticos del mismo formulario (mismo
conjunto/torre/apartamento, mismo residente nombre+teléfono) crean 3 filas
de `Ocupante` activas para la misma persona en el mismo apartamento (solo la
primera queda `es_principal`). Esto es fácil de disparar en el uso real: el
staff repite el trámite de "declarar la unidad" para anunciar un paquete
nuevo a alguien que ya vive ahí, o hace doble clic en "Guardar".

Impacto: el roster muestra a la misma persona repetida varias veces (en
`/mis-datos` "Mis Ocupantes"/"Quién más vive acá" y en `/residentes/{id}`),
y cada duplicado consume un cupo del límite de 5 Ocupantes activos por
apartamento sin que nadie nuevo se haya agregado en realidad.

`/mis-datos` (cliente) SÍ tiene esta guardia de idempotencia (ticket 01,
`.scratch/mis-datos`) -- a `/announce` (staff) le falta el equivalente.

## Alcance del fix

Solo `announce_new.py` -- antes de llamar `agregar_ocupante` por cada fila,
si ya existe un Ocupante ACTIVO de esa misma unidad para esa Persona (con
teléfono) o ese nombre normalizado (sin teléfono), se salta esa fila en vez
de crear un duplicado. No se toca `agregar_ocupante` ni las demás vías que
ya lo llaman una fila a la vez (`/mis-datos/ocupantes`,
`/residentes/{id}/ocupantes`) -- ahí cada clic es una intención explícita
de una persona a la vez, agregar una guardia por-nombre ahí podría bloquear
silenciosamente un alta legítima (dos residentes que comparten nombre).

## Implementación

`announce_new.py`: antes del loop de residentes, se toma el roster activo
del apartamento (`listar_ocupantes`). Por fila:
- **Con teléfono**: resuelve la Persona (`get_or_create_persona`, idempotente
  -- no crea de más) y chequea `ocupante_de_persona(db, apto, persona.id)`;
  si ya es Ocupante activo de esta unidad, se salta la fila.
- **Sin teléfono**: compara el nombre normalizado contra los nombres de
  Ocupantes sin teléfono ya activos en la unidad (recalculado sobre la
  marcha para tampoco duplicar dentro del MISMO envío si el staff repite un
  nombre en dos filas).

Regresión: `test_reenviar_el_mismo_residente_no_duplica_el_ocupante` y
`test_reenviar_un_residente_sin_telefono_no_duplica_el_ocupante` en
`test_announce_new.py` -- confirmadas en rojo antes del fix (creaban 3 y 4
filas respectivamente en vez de 1 y 2), verdes después. Suite completa:
541 passed (1 fallo intermitente preexistente y no relacionado en
`test_otp_service.py`, ya documentado, pasa limpio al reintentar solo).
