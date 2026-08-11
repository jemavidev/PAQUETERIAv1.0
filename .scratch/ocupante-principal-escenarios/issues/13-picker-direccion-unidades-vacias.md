# 13 — Picker de tab Dirección: solo unidades vacías

**What to build:** el picker de Torre+Apartamento en tab "Dirección" de `/residentes/{id}` deja de ser informativo (punto ámbar, igual seleccionable) y pasa a deshabilitar cualquier unidad con al menos un Ocupante activo (con o sin principal confirmado) — solo se pueden elegir unidades completamente vacías desde ahí. Agregar más residentes a una unidad que ya tiene gente sigue disponible, pero exclusivamente desde tab Residentes. Además, cuando `reasignar_apartamento` detecta y limpia un `apartamento_actual_id` huérfano, se muestra un mensaje explicando qué se corrigió.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Nueva consulta de dominio (más amplia que `apartamentos_con_principal`): unidades con AL MENOS un Ocupante activo, tenga o no principal confirmado.
- [ ] El picker de tab Dirección deshabilita (no solo marca) esas unidades — se puede ver que existen pero no seleccionarlas.
- [ ] Intentar enviar una unidad ocupada de todos modos (POST directo) sigue rechazándose server-side con el mensaje ya existente.
- [ ] Al limpiar un `apartamento_actual_id` huérfano (sin Ocupante real detrás), la respuesta incluye un mensaje explicando la limpieza.
- [ ] Tests en `test_customers_manage.py` cubriendo: unidad vacía seleccionable, unidad ocupada deshabilitada en el picker y rechazada si se fuerza por POST, mensaje de dato huérfano.
