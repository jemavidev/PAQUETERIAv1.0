# 170 — Eliminar el campo `segundo_contacto`

**Pedido original:** "En la vista de /residentes, en el tab de 'Datos', existe un input llamado
'segundo_contacto', no he visto que se use y no creo que se vaya a utilizar, dime si es requerido
en algún flujo, de lo contrario lo vamos a remover o eliminar" → confirmado: "si procede con la
eliminacion."

**Status:** implementado

## Diagnóstico

Se investigó cada referencia en `src/`, `tests/` y `alembic/` antes de tocar nada. `segundo_
contacto` NUNCA se leía en ningún flujo crítico (notificaciones, OTP, `announce()`) — el único uso
real era como término extra de búsqueda en `/residentes` (`_buscar_residentes`), y ni siquiera
estaba expuesto al cliente en `/mis-datos` (solo en la ficha de staff). Confirmado seguro de
eliminar por completo, no solo ocultar.

## Cambio

- `persona.py`: columna `segundo_contacto` eliminada del modelo `Persona`.
- `persona_service.py`: parámetro y manejo de `segundo_contacto` eliminados de `update_datos_
  personales`; línea `persona.segundo_contacto = None` eliminada de `anonimizar_persona`.
- `customers_manage.py`: filtro `Persona.segundo_contacto.ilike(...)` eliminado de `_buscar_
  residentes` (y su mención en el docstring); parámetro eliminado de `customers_manage_update`.
- `detail.html`: input `segundo_contacto` eliminado del form de tab "Datos".
- Migración `0031_eliminar_segundo_contacto.py`: `DROP COLUMN personas.segundo_contacto`.

## Verificación

- Tests actualizados/eliminados en los archivos que referenciaban el campo (`test_persona_
  service.py`, `test_anonimizar_persona.py`, `test_customers_manage.py`).
- Suite completa: 1071/1071 (`bgvtcw93y`), incluye `test_parity_esquema_orm.py` confirmando que
  ORM y migraciones no divergieron.
- Verificado en vivo contra `localhost:8010`: tab "Datos" ya no muestra el input, guardar el resto
  de los campos de esa tab sigue funcionando.
