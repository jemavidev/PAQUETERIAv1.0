# 04 — Mecanismo SSH+allowlist para aplicar credenciales

**What to build:** la pieza de infraestructura que hace posible cambiar una
credencial real desde la app sin abrir un socket de Docker ni pasar secretos por un
log de GitHub Actions — una función que valida y despacha un cambio de `.env` al
servidor por SSH, con una llave restringida a una sola operación. Sin UI todavía —
este ticket es el seam de infraestructura que el ticket 05 va a consumir.

Ver `.scratch/administracion-proveedores/spec.md` (User Stories 6, 9, 10, 15, 16,
23; Implementation Decisions "Mecanismo de aplicación de credenciales"; Out of Scope
para las alternativas descartadas — GitHub Actions, socket de Docker).

**Blocked by:** 01 (deriva el allowlist del catálogo de proveedores en código)

**Status:** ready-for-agent

- [ ] Función `aplicar_credenciales_proveedor(cambios: dict[str, str]) -> None` (o
      firma equivalente) en un módulo de infraestructura nuevo, fuera de
      `app/domain` (habla con un proceso externo por SSH, mismo criterio de límite
      que ya separa `sns_sender.py`/`liwa_sender.py` de la lógica pura de dominio).
- [ ] Valida cada clave de `cambios` contra el allowlist derivado del catálogo de
      proveedores del ticket 01 ANTES de intentar cualquier conexión — una clave
      fuera del allowlist se rechaza sin tocar la red (defensa en profundidad, no
      confía solo en el `command=` del servidor).
- [ ] Se conecta por SSH con una llave dedicada (nueva variable de entorno para la
      ruta/contenido de la llave), ejecuta el comando remoto, y propaga cualquier
      fallo (timeout, conexión rechazada, comando remoto con código de salida
      distinto de cero) como una excepción clara — nunca un éxito silencioso.
- [ ] El payload enviado al comando remoto tiene el formato exacto que espera el
      script del ticket 06 (documentar el contrato explícitamente en el docstring del
      módulo, ya que viven en repos/lugares distintos).
- [ ] Tests (`tests/domain/test_deploy_ssh.py` o ubicación equivalente): la
      conexión SSH real está mockeada (nunca toca red ni un servidor real);
      casos cubiertos — clave fuera del allowlist rechazada sin conectar; fallo de
      conexión propaga excepción; fallo del comando remoto (código de salida
      distinto de cero) propaga excepción; caso de éxito no lanza nada.
