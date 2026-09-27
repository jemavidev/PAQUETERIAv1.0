# 379 — "Primera entrega" no funciona para un cliente identificado solo por usuario de WhatsApp

**Reporte original (Jesús):** "no es posible ahora diferenciar entre un cliente que recibe un paquete por primera vez
y por ende aparece un cobro" — tras el análisis: "en caso que sea con teléfono sí funciona, pero si es con usuario de
WhatsApp no funciona".

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Diagnóstico

No es una regresión de [[377]]/[[378]]. La regla de primera entrega (`es_primera_entrega_a_telefono`,
`paquete_service.py`; su versión batch en `packages.py::_listar`; el cobro real en `deliver_action`; `/consultar`)
identifica al cliente SOLO por `Paquete.recipient_phone`, y sin teléfono responde "no es primera". ADR-0007 permitió
Personas solo-WhatsApp, pero el Paquete ni siquiera guarda el WhatsApp del destinatario. Resultado para un cliente
solo-WhatsApp (sin Principal con teléfono en su unidad): nunca aparece la bandera "Primera entrega a este cliente" y se
le cobra la tarifa base desde el primer paquete (NPJN: $1.500 en su primera entrega); las estadísticas de exenciones
tampoco lo cuentan. BD dev: 55 paquetes sin `recipient_phone`.

## Decisiones

1. Nueva columna `Paquete.recipient_whatsapp` (snapshot, ADR-0001): el usuario de WhatsApp PROPIO del destinatario
   (sin fallback al Principal). Se llena al anunciar, al corregir el destinatario (candidato o "Nuevo residente") y al
   sincronizar hermanos. Migración: agrega la columna (+ índice) y la llena en los paquetes sin teléfono cuyo
   destinatario es el propio Anunciante (mismo nombre).
2. Regla única: con `recipient_phone`, se decide por teléfono (sin cambios); sin teléfono pero con
   `recipient_whatsapp`, primera entrega = ningún ENTREGADO previo con ese WhatsApp; sin ninguno, no se puede verificar.
3. Sin teléfono ni WhatsApp: se cobra como hoy (decisión por defecto, recomendada), y el modal Entregar lo avisa: "No se
   puede verificar si es la primera entrega (sin teléfono ni WhatsApp)".

## Verificación

- `tests/web/test_primera_entrega_whatsapp.py` (9): anunciar por WhatsApp guarda `recipient_whatsapp`; primera entrega
  por WhatsApp muestra la bandera y cobra base $0; segunda entrega al mismo WhatsApp cobra y sin bandera; otro WhatsApp
  no cuenta como previa; `/consultar` también muestra la bandera; sin teléfono ni WhatsApp cobra y avisa; con teléfono
  sin aviso; corregir destinatario a un residente solo-WhatsApp copia su WhatsApp; la migración llena los paquetes para
  el propio Anunciante.
- Regresión: `tests/data_model` (833) y `tests/web` completo (1200) en verde.
- BD dev: `alembic upgrade head` aplicó `0058`; NPJN y ATN5 quedaron con su WhatsApp; 50 paquetes sin teléfono ni
  WhatsApp (destinatarios "solo nombre" de los datos demo) se cobran con el aviso.
- Limitación conocida (sin cambios, issue 314): un residente solo-WhatsApp cuyo paquete tomó como `recipient_phone` el
  teléfono del Principal de su unidad sigue juzgándose por ese teléfono.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar en vivo". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
