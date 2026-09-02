# 06 — Aprovisionar el script remoto + `authorized_keys` restringido en el servidor

**What to build:** la mitad de la Fase 2 que vive FUERA de este repo — el script en
el servidor de `test.papyrus.com.co` que el mecanismo del ticket 04 invoca por SSH, y
la restricción de la llave que lo hace seguro. Es trabajo de infraestructura/ops, no
un PR de código Python — puede avanzar en paralelo al ticket 05, ya que ambos solo
dependen del contrato definido en el ticket 04.

Ver `.scratch/administracion-proveedores/spec.md` (Implementation Decisions "Script
remoto en el servidor"; Further Notes sobre por qué este script no se despliega vía
git).

**Blocked by:** 04 (necesita el contrato/protocolo exacto del payload)

**Status:** verificado -- de punta a punta contra el servidor real, 2026-09-02. Ver
`docs/ops/deploy-ssh-credenciales.md` para el detalle completo (contenido del
script, `authorized_keys`, y los tres bugs encontrados/corregidos en la
verificación en vivo).

- [x] Script en el servidor (`update_provider_env.sh`) que lee pares `KEY=VALOR` de
      stdin en el formato exacto que define el ticket 04.
- [x] Rechaza cualquier `KEY` fuera del allowlist explícito de variables de
      proveedor (la misma lista derivada del catálogo de código) — sale con error sin
      tocar `.env` si encuentra una clave no permitida.
- [x] Actualiza (o agrega) solo esas líneas específicas en `.env`, sin tocar el resto
      del archivo (comentarios, otras variables).
- [x] Corre `docker compose --env-file .env up -d` (sin `--build`, ya que ningún
      código cambia) para que el contenedor recargue las variables nuevas -- en
      segundo plano (ver Bug 3 en `docs/ops/deploy-ssh-credenciales.md`: en primer
      plano mataba con SIGKILL la petición HTTP que disparó el cambio, porque el
      contenedor que se reinicia es el mismo que sirve esa petición).
- [x] Entrada nueva en `authorized_keys` del servidor con `command="..."` forzado a
      ejecutar SOLO este script — la llave no puede abrir una shell libre ni ejecutar
      ningún otro comando (`no-pty,no-agent-forwarding,no-X11-forwarding,
      no-port-forwarding,no-user-rc`).
- [x] Prueba manual documentada (ver `docs/ops/deploy-ssh-credenciales.md`, sección
      "Pruebas manuales"): una clave dentro del allowlist se aplica de verdad (no
      solo "exit 0" -- verificado que el valor realmente cambia en `.env`) y el
      contenedor recarga solo, sin intervención manual; una clave fuera del allowlist
      se rechaza sin tocar `.env`; la restricción de `authorized_keys` impide
      cualquier uso de la llave fuera del script forzado por construcción.
- [x] El script y la configuración de `authorized_keys` quedan documentados en
      `docs/ops/deploy-ssh-credenciales.md` -- contenido completo del script,
      cómo reaprovisionar desde cero si el servidor se reconstruye.
