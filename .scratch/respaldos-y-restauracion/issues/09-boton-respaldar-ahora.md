# 09 — Botón "Respaldar ahora"

**What to build:** en la pantalla "Respaldos", un botón que lanza un respaldo con motivo "a pedido" (registrando
quién) en segundo plano, fuera de la petición web. La pantalla muestra si está en curso, si terminó bien o si falló; el
estado se guarda en la base de datos para sobrevivir a reinicios. No puede correr a la vez que otro respaldo.

**Blocked by:** 04, 08

**Status:** ready-for-agent

- [ ] El botón responde de inmediato y el respaldo sigue aunque se cierre la pantalla.
- [ ] Estado en curso / terminado / falló visible y persistente tras un reinicio de la app.
- [ ] El respaldo queda en `puntual/` con "a pedido de <usuario>" en el manifiesto.
- [ ] Si ya hay un respaldo en curso, el botón lo dice en vez de lanzar otro.
- [ ] Pruebas HTTP: lanza, reporta estado, rechaza un segundo simultáneo, solo ADMIN.
