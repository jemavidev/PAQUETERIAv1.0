# 91 — `/paquetes` modal Ver: título con código de acceso + botón de estado más chico

**Pedido original (cliente):**
"vamos a hacer un cambio al modal de clientes, necesito que esto
'WIZARD RETEST 4DIGIT' quede al aldo de el codigo 'NBXY', para este
ejemplo deberia verse asi 'WIZARD RETEST 4DIGIT - NBXY', la finalidad
de esto es que se compacte un poco mas la parte superior de este
modal. Adicional necesito que 'modal-receive-<id>' sea un poco mas
pequeno, posiblemente que el pading o margin sea menor, de esta forma
tener esa seccion superior mas pequena, recuerda que este boton
deberia ser lo suficientemente grande para su look and feel."

**Status:** implementado

## Implementación

- `packages/_resultados.html`, modal "Ver": el título pasa de solo
  `p.recipient_name` a `p.recipient_name ~ " - " ~ p.access_code`
  (ej. "WIZARD RETEST 4DIGIT - NBXY") -- el chip de código de acceso
  que vivía aparte, en la fila del badge/Dirección, se elimina de ahí
  (ya está en el título, no hace falta repetirlo).
- El botón de siguiente estado (Recibir en ANUNCIADO, Entregar en
  RECIBIDO) baja de 72px (doblado el 2026-08-15) a **56px** -- un
  punto intermedio entre el tamaño original (36px) y el doblado,
  manteniendo el look and feel prominente que pidió conservar.

## Verificación

- Playwright (Chromium headless) contra el servidor local real:
  confirmado el título compuesto y el botón más chico en un paquete
  ANUNCIADO (botón "Recibir") y en uno RECIBIDO (botón "Entregar").
- `tests/web/test_packages.py`: 95 tests pasan.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
