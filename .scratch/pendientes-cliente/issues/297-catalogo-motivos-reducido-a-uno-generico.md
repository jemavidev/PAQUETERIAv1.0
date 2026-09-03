# 297 — Catálogo de motivos de cancelación reducido a un solo motivo genérico

**Pedido original (cliente):** "porque tantas opciones para cada motivo de
cancelacion, creo que con uno solo esta mas que bien, ya que este podria
contener el motivo real de cancelacion o no" — tras ver [[296]] ya
implementado, con los 4 motivos sembrados por `.scratch/motivos-
cancelacion-catalogo` (Anuncio erróneo, Devuelto al transportador, No
reclamado, Otro) cada uno como su propio módulo (fila + modal de 3
canales).

**Status:** implementado -- pendiente confirmar en vivo en test.papyrus.com.co

## Alcance acordado

- Se borran del catálogo "Anuncio erróneo", "Devuelto al transportador" y
  "No reclamado", dejando únicamente "Otro".
- "Otro" es el que sobrevive a propósito (no un motivo nuevo con otro
  nombre): su comportamiento de texto libre en el modal "Cancelar
  paquete" de `/paquetes` ya está hardcodeado al literal "Otro" (JS de
  `packages/_resultados.html` + `cancel_action` en `packages.py`) --
  conservarlo evita tocar esa lógica ya probada, y ya cumple exactamente
  lo pedido: captura la razón real si el staff la escribe, o queda
  genérico si no.
- El CRUD unificado en [[296]] sigue existiendo intacto -- el ADMIN puede
  agregar motivos de nuevo más adelante si hace falta, esto es solo un
  cambio de los datos sembrados, no de la funcionalidad.

## Implementación

- Migración nueva `0040_motivos_solo_otro` (descendiente de `0039`, no se
  reescribió esa migración ya aplicada) -- borra las 3 etiquetas, `Paquete.
  cancel_reason`/`PlantillaNotificacion.motivo` de paquetes/plantillas ya
  existentes con esos motivos quedan intactos (no son FK al catálogo,
  mismo criterio ya documentado en `motivo_cancelacion_service.
  eliminar_motivo`).
- Aplicada y verificada contra el Postgres de desarrollo real
  (`paquetex_dev_pg`, con backup previo), no solo el efímero de tests --
  igual que `0039`.
- Tests que asumían 4 motivos/7 filas actualizados: `tests/web/
  test_admin_notificaciones.py` (conteos 7→4, 14→8, 21→12),
  `tests/web/test_notifications.py` y `tests/web/test_packages.py`
  (2 tests que cancelaban con "Anuncio erróneo"/"Devuelto al
  transportador" pasan a usar "Otro"; el test que verificaba las 4
  etiquetas en el modal pasa a verificar solo "Otro").
