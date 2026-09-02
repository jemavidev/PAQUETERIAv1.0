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

**Status:** implementado -- sin caller todavía (issue 05), no hay nada que verificar
en vivo hasta que la pantalla lo use de verdad.

- [x] `app/infra/deploy_ssh.py::aplicar_credenciales_proveedor(cambios: dict[str,
      str]) -> None` -- módulo nuevo `app/infra/` (fuera de `app/domain`, respeta el
      aislamiento del rebuild, ADR-0004).
- [x] Valida cada clave de `cambios` contra `proveedores_catalogo.variables_
      permitidas()` (el allowlist del catálogo del ticket 01) ANTES de instanciar
      `paramiko.SSHClient` — una clave fuera del allowlist se rechaza sin tocar la red.
- [x] Se conecta con `paramiko` (dependencia nueva, `requirements.txt`) usando
      `DEPLOY_SSH_HOST`/`DEPLOY_SSH_KEY_PATH`/`DEPLOY_SSH_USER` (opcional, default
      `ubuntu`); host key verificada contra `known_hosts` del sistema con
      `RejectPolicy` (falla cerrado ante host desconocido, nunca lo agrega solo).
      Cualquier fallo (config incompleta, timeout, conexión rechazada, código de
      salida remoto ≠0) se propaga SIEMPRE como `ErrorAplicandoCredenciales` — un
      solo tipo de excepción, nunca un éxito silencioso.
- [x] Contrato del payload documentado en el docstring del módulo (`CLAVE=VALOR\n`
      por línea, sin líneas en blanco, valor sin saltos de línea) para el script
      remoto del ticket 06, que vive en un repo distinto.
- [x] `tests/infra/test_deploy_ssh.py` (8 tests, SSH mockeado, nunca toca red): los
      4 casos exactos del ticket + 2 extra que salieron del code review (config SSH
      incompleta, `cambios` vacío no conecta).

**Decisión de librería (no estaba en el ticket):** `paramiko` (SSH puro-Python) en vez
de `subprocess`+binario `ssh` del sistema -- evita instalar `openssh-client` en la
imagen Docker del repo de deploy (cambio de infraestructura cruzado, fuera de este
repo); el costo es una dependencia nueva en `requirements.txt`.

**Nota para issue 06:** el `known_hosts` del servidor SSH y la llave privada deben
quedar provisionados en la imagen/contenedor de la app (ej. `ssh-keyscan` en el build)
-- sin eso, `aplicar_credenciales_proveedor` falla cerrado con `ErrorAplicandoCredenciales`
en vez de conectar.

**Code review** (Standards + Spec): 3 hallazgos confirmados -- (1) `os.environ[...]`
directo lanzaba `KeyError` crudo si faltaban las variables de SSH, rompiendo el
contrato de un solo tipo de excepción; extraído a `_config()`, mismo patrón que
`liwa_sender._config()`. (2) `_armar_payload({})` producía una línea en blanco,
violando el propio contrato documentado; corregido + `cambios` vacío ahora ni
siquiera conecta. (3) 4 clases falsas en los tests colapsadas a 2 (`_EjecucionFalsa`
+ `_ClienteSshFalso`), más cerca del "un doble por límite externo" que ya usan
`test_sns_sender.py`/`test_liwa_sender.py`.

**Verificación:** suite completa (1298 passed) tras los fixes del code review.
