# 12 — Toggle "autorización automática de recepción" en Datos personales

**What to build:** nuevo booleano `Persona.autoriza_recepcion_automatica` (default `False`), con su propio toggle sí/no en la sección "Datos personales" de `/mis-datos` — disponible para cualquiera que llegue a ver esa vista (principal u Ocupante-con-teléfono, ambos tienen teléfono propio por construcción). Es **puramente informativo/visible para el staff** (ej. en `/residentes/{id}`): indica que esa persona ya autorizó de antemano que el staff anuncie/reciba paquetes a su nombre sin necesidad de llamarla primero para pedir permiso verbal. **No es un gate técnico** — el staff ya puede anunciar/recibir para cualquiera sin restricción alguna hoy (`/announce`), y esto no cambia nada de esa capacidad; es solo una señal para su proceso humano/manual.

**Blocked by:** Ninguno — puede empezar de inmediato, independiente del sistema de Ocupantes.

**Status:** done

- [x] Nueva columna `Persona.autoriza_recepcion_automatica` (migración Alembic), default `False`.
- [x] Toggle visible y editable en "Datos personales" de `/mis-datos`.
- [x] El valor se muestra en `/residentes/{id}` para que el staff lo vea.
- [x] No bloquea ni habilita ninguna acción del staff — `/announce` y `/paquetes/{id}/recibir` no se tocaron en este ticket.
- [x] Tests cubren: guardar el toggle (marcar/desmarcar), default apagado, mostrarlo correctamente en la ficha de staff.

## Implementación

- `alembic/versions/0019_persona_auto_recepcion.py` (nombre acortado — el id de revisión no cabía en la columna `alembic_version.version_num`, `VARCHAR(32)`).
- `Persona.autoriza_recepcion_automatica` + `persona_service.set_autoriza_recepcion_automatica`.
- `customer_verify.py`: checkbox con semántica "ausente = False" (igual que la matriz de preferencias), no vía `update_datos_personales`.
- `customer/verify.html` (checkbox) + `customers_manage/detail.html` (solo lectura, con leyenda distinta según el estado).
- 2 tests de dominio + 3 web (cliente) + 2 web (staff). Suite completa: 526 passed.
