# 166 — Principal viejo (ya desvinculado) bloqueaba la promoción para siempre

**Pedido original:** "he realizado unos movimientos de residentes entre apartamento, y veo que
después del movimiento que le hice a 'DANIELA ARRAZOLA', esta no se cambió a principal, incluso
sabiendo que ya tiene asociado apartamento y un teléfono/whatsapp, dime qué pudo haber pasado" →
confirmado el diagnóstico, pedido explícito de corregirlo: "solucionalo según tu recomendación."

**Status:** verificado

## Diagnóstico

Bug real, dos capas:

1. **Python** -- `confirmar_ocupante` y `promover_al_recibir` deciden si una unidad "ya tiene
   Principal" con una consulta que buscaba `Ocupante.es_principal.is_(True)` SIN filtrar
   `desvinculado_en IS NULL`. Un Ocupante dado de baja conserva `es_principal=True` como registro
   histórico (`dar_de_baja_ocupante` nunca lo limpia) -- así que una unidad que alguna vez tuvo
   Principal, y luego se vació por completo, quedaba "atascada" para siempre: nadie nuevo podía
   volver a promoverse ahí automáticamente.
2. **Base de datos** -- al corregir el punto 1, apareció una `UniqueViolation` real: el índice
   único `uq_ocupantes_principal_por_apartamento` (que garantiza "máximo 1 Principal por
   Apartamento" a nivel de BD) tampoco filtraba `desvinculado_en IS NULL` -- mismo bug, una capa
   más profunda. El índice hermano `uq_ocupantes_persona_activo` (0024) sí lo filtraba desde el
   inicio; este no.

Confirmado con los datos reales de Daniela en la base de desarrollo: su unidad actual (Torre
2 · Apto 302) había tenido antes a otro residente como Principal, ya desvinculado -- esa fila
vieja seguía bloqueando cualquier promoción nueva en esa unidad.

## Cambio

- `confirmar_ocupante`/`promover_al_recibir` (`ocupante_service.py`): agregado
  `Ocupante.desvinculado_en.is_(None)` a la consulta `hay_principal` de las 2 funciones.
- `Ocupante.__table_args__`: el índice `uq_ocupantes_principal_por_apartamento` pasa de
  `WHERE es_principal` a `WHERE es_principal AND desvinculado_en IS NULL`.
- Migración `0030_ocupante_principal_activo`: recrea el índice en la base real (drop + create,
  mismo patrón que otras migraciones de esquema de este repo).

## Verificación

- 2 tests nuevos (`test_confirmar_promueve_aunque_hubo_un_principal_viejo_ya_desvinculado` en
  `test_ocupante_service.py`, `test_recibir_promueve_aunque_la_unidad_tuvo_un_principal_viejo_ya_
  desvinculado` en `test_promocion_automatica.py`) -- ambos reproducen el escenario exacto
  (Principal viejo dado de baja, unidad vacía, alguien nuevo llega) y confirman que SÍ se
  promueve ahora.
- `test_parity_esquema_orm.py` (guard de que el modelo ORM y las migraciones no diverjan): sigue
  en verde con el índice corregido en ambos lados.
- Suite completa: 1069/1069.
- Verificado en vivo contra `localhost:8010`: reproducido el escenario completo (un residente
  Principal se va de una unidad, otro residente nuevo la recibe) -- confirmado que el nuevo queda
  Principal, sin el error de índice único. Datos de prueba limpiados.
