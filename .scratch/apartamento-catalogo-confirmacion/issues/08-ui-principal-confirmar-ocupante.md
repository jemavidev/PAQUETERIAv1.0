# 08 — UI principal: confirmar/rechazar Ocupantes pendientes en `/mis-datos`

**What to build:** la tarjeta "Mis Ocupantes" en `/mis-datos` (ya construida, ticket 03 de `.scratch/mis-datos/`), visible solo para el Ocupante principal ya confirmado de un apartamento, muestra el estado pending/confirmado de cada Ocupante de su unidad y agrega acciones "Confirmar"/"Rechazar" para los pending, usando las mismas funciones de dominio del ticket 06. Además, si la propia Persona logueada tiene una asociación pending (no solo confirmada), `/mis-datos` se lo muestra — sabe que ya puede usar el sistema con normalidad pero que su reclamo sigue sin verificar.

**Blocked by:** 06.

**Status:** done

- [x] El principal ve el estado pending/confirmado de cada Ocupante de su unidad (badge Principal/Confirmado/Pendiente de confirmar en "Mis Ocupantes").
- [x] El principal puede confirmar un pending de su propia unidad.
- [x] El principal puede rechazar un pending de su propia unidad — reusa la ruta `/baja` ya existente (mismo patrón que el ticket 07), sin ruta nueva.
- [x] Un residente cuya propia asociación está pending lo ve reflejado en `/mis-datos` (aviso informativo en la pestaña "Mi apartamento"), sin que eso le bloquee ninguna otra función de la pantalla (probado explícitamente: guardar el nombre sigue funcionando igual).
- [x] Un principal no puede confirmar/rechazar Ocupantes de un apartamento que no es el suyo (403 vía `_ocupante_gestionable_por`, ya existente, reusado tal cual).
- [x] Tests web en `test_customer_verify.py` cubren confirmar, rechazar, ver el propio estado pending (y que desaparece al confirmarse), y el 403 cruzado entre apartamentos ajenos.

## Bug real encontrado y corregido: el boundary `es_ocupante_no_principal`

Documentado como pendiente en el ticket 06 — resuelto acá. `es_ocupante_no_principal` decidía "solo lectura" mirando `not mi_ocupante.es_principal`, lo cual antes del ticket 06 nunca capturaba al declarante inicial (auto-promovido de inmediato). Con confirmación, cualquier residente recién auto-declarado (pending, único en su unidad) caía en esa condición y veía "esto lo gestiona el principal de tu unidad" — un principal que ni existe.

**Primer intento (equivocado):** cambiar la condición a "¿mi apartamento ya tiene un Ocupante confirmado como principal?" — pero esto fallaba distinto: un SEGUNDO Ocupante agregado por otra persona (ambos todavía pending, nadie confirmado aún) quedaba con acceso de edición completo sobre Torre/Apartamento, aunque no se auto-declaró él, lo agregó alguien más. Atrapado por un test ya existente (`test_ocupante_no_principal_no_puede_cambiar_torre_apartamento`) que dejó de pasar con ese primer intento.

**Fix correcto:** la pregunta relevante no es si ya hay un principal *confirmado*, sino si hay **algún otro Ocupante activo** en la unidad, esté o no confirmado. Solo lectura cuando SÍ hay alguien más (alguien más está coordinando la unidad, confirmado o no); edición normal cuando sos el único (nadie más a quien pisarle la gestión, sin importar tu propia confirmación).

## Implementación

- **Web:** `customer_verify.py` — `_hay_otro_ocupante_activo` reemplaza el cálculo viejo de `es_ocupante_no_principal`; nuevo campo de contexto `mi_reclamo_pending` (independiente del anterior, puramente informativo). Ruta nueva `POST /mis-datos/ocupantes/{ocupante_id}/confirmar`, mismo guard `_ocupante_gestionable_por` que ya usan `/baja` y `/promover`.
- **Template:** `customer/verify.html` — aviso ámbar informativo en la pestaña "Mi apartamento" cuando `mi_reclamo_pending`; badge de 3 estados + botón "Confirmar" en la tarjeta "Mis Ocupantes" (mismo patrón visual que el ticket 07 del lado staff).
- **Tests:** 5 nuevos (confirmar, rechazar, 403 cruzado, ver el propio pending sin bloqueo, el aviso desaparece al confirmarse) + 2 tests preexistentes corregidos para reflejar el fix del boundary.
- **Suite completa:** verde salvo los 6 fallos preexistentes de `test_layout.py` (confirmado en el ticket 01).
