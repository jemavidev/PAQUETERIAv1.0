# 76 — Ambiente local de desarrollo (testing manual más rápido)

**Pedido original (cliente):** "quiero que me ayuden a intentar hacer
testing manual (echo por me, cargando paginas, ingresando clientes y
modificando lo que construyes), pero de una forma mas rapida, creo que
podria generar todo un esquema completo para correr el proyecto en
localhost y solo poder desplegar a test cuando te lo pida."

**Status:** implementado

## Contexto

Hasta ahora, la única forma de ver un cambio en un navegador real era
esperar el ciclo completo de deploy a `test.papyrus.com.co` (push → CI →
build → deploy, ~5 min) -- o, para mi propia verificación, un Postgres
efímero descartable por ticket (`tests/_harness.py`).

## Implementación

- `CODE/scripts/paquetex_dev_up.sh`: levanta (o reusa) un Postgres
  persistente dedicado (`paquetex_dev_pg`, puerto 5433, volumen CON
  NOMBRE `paquetex_dev_pgdata` para que nunca quede huérfano), migra,
  siembra un admin (`admin@local.test` / `Contrasena1`) solo si la base
  está vacía, y deja `uvicorn --reload` corriendo en
  `http://localhost:8010`. Cambios de código y templates se reflejan al
  instante, sin rebuild de imagen (se descartó `docker-compose` completo
  por ser más lento para este ciclo).
- `CODE/scripts/paquetex_dev_reset.sh`: borra contenedor + volumen para
  volver a datos limpios.
- Acuerdo de flujo hacia adelante: dejar de desplegar automáticamente a
  `test.papyrus.com.co` al terminar cada cambio -- probar primero en local,
  desplegar solo cuando el cliente lo pida explícitamente (reemplaza la
  regla anterior de auto-deploy, ver memoria `deploy-solo-cuando-se-pide`).

## Verificación

- Corrida real de `paquetex_dev_up.sh`: migración completa (28 revisiones)
  sin errores, admin sembrado, login + `/paquetes` responden 200.
- `--reload` confirmado: tocar un archivo `.py` dispara el log
  "WatchFiles detected changes... Reloading..." y el servidor vuelve a
  responder sin intervención manual.
- Postgres queda corriendo tras apagar `uvicorn` (Ctrl+C) -- persistencia
  confirmada entre corridas.
