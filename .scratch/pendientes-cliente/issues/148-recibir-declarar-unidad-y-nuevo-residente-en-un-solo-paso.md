# 148 — "Recibir": declarar unidad nueva + registrar residente en un solo paso

**Pedido original:** el cliente probó en vivo declarar "Torre 10 · Apt 302" al recibir un paquete de
un destinatario sin apartamento, esperando que quedara registrado como Residente Principal de esa
unidad -- no pasó. Pidió análisis ("analiza y dime qué pasó") y luego el fix ("arréglalo para que
funcione en un solo paso").

**Status:** implementado

## Qué pasaba (diagnóstico)

`receive_action` (`packages.py`) siempre tuvo DOS sub-pasos independientes y opcionales: (1)
declarar unidad (`corregir_apartamento`, solo toca el snapshot del Paquete) y (2) resolver "¿A
nombre de quién es?" (`candidato_idx`/`nuevo_ocupante_nombre`, el único que crea/toca un Ocupante
real vía `agregar_ocupante`). El backend YA encadenaba los dos correctamente en un mismo request
(sección 2 corre después de que sección 1 actualiza el snapshot en memoria). El bloqueo era 100%
de la plantilla: `modal_recibir` escondía la sección 2 ENTERA (`{% if candidatos and not
sin_apartamento %}`) mientras el paquete no tuviera unidad -- decisión deliberada de conversación
2026-08-17, para evitar un bug real: `candidatos_correccion` computado ANTES de declarar la
unidad devuelve el Anunciante como único "candidato" (índice 0); si esa lista se hubiera
mostrado y el staff TAMBIÉN declaraba una unidad nueva en el mismo envío, el servidor recalcula
`candidatos_correccion` con la unidad YA declarada -- el índice 0 podía terminar apuntando a otra
persona real de esa unidad, no al Anunciante que el staff vio en pantalla.

Consecuencia real: un paquete podía quedar Recibido con dirección pero SIN ningún Ocupante creado
-- exactamente el caso reportado (Torre 10/302 con `recipient_name` pero cero Ocupantes, ninguna
Persona con `apartamento_actual_id` asignado).

## Fix

`components/_recibir_paquete.html`: la sección "¿A nombre de quién es?" ahora SÍ se muestra
cuando `sin_apartamento`, pero **sin los candidatos numerados** (el riesgo real de arriba sigue
evitado, no removido) -- solo la opción "Nuevo residente", que es segura sin importar el orden:
no depende de ningún índice, `agregar_ocupante` resuelve contra `paquete.snapshot_torre/
apartamento` tal como quedaron DESPUÉS del picker, en el mismo request. Cero cambios en
`packages.py` -- el backend ya estaba listo, solo hacía falta que la plantilla se lo ofreciera al
staff.

Elegir un residente YA EXISTENTE de una unidad recién declarada (a diferencia de crear uno nuevo)
sigue sin ofrecerse en el mismo paso -- eso requeriría los candidatos numerados que justamente se
siguen evitando por el riesgo de arriba. El picker ya informa (nombres reales) si la unidad
elegida no está vacía; para asociar a alguien puntual de esa lista sigue haciendo falta "Corregir
destinatario" después (mismo criterio ya usado: "lo ambiguo espera al segundo paso").

Descubrimiento relevante en el camino: `paquete_lifecycle.receive()` YA dispara
`promover_al_recibir` (ticket 04) -- si el Ocupante destinatario recién creado no tiene principal
en su unidad, lo promueve y confirma en el mismo acto. Esa pieza siempre existió; lo único que
faltaba era que el Ocupante llegara a crearse.

## Verificación

- `tests/web/test_packages.py::test_recibir_declara_unidad_nueva_y_registra_residente_en_un_solo_envio`
  (nuevo): declara Torre 10/302 + nuevo residente con contacto en un solo POST -- Paquete RECIBIDO
  con snapshot correcto, Ocupante creado **ya confirmado y principal** (gracias a
  `promover_al_recibir`).
- Suite completa `/paquetes` + `/announce` + `/residentes`: 327/327, sin regresiones (el guard de
  índice que motivó el diseño original se preserva -- ningún test de candidatos numerados con
  `sin_apartamento` cambió de comportamiento).
- Reproducido en vivo contra `localhost:8010`: Torre 10/305 (unidad vacía), un solo POST con
  `torre`+`apartamento`+`candidato_idx=nuevo`+`nuevo_ocupante_nombre`+`nuevo_ocupante_contacto` →
  Paquete RECIBIDO, Ocupante creado con `es_principal=True`/`confirmado_en` seteado, visible de
  inmediato en `/residentes` con badge "Principal".
