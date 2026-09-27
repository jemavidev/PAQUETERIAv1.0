# 393 — Saldo contra entrega: el destinatario nunca se adivina por un nombre repetido

**Pedido original (Jesús):** "si arréglala" -- sobre el riesgo señalado al explicar el saldo por apartamento: el
destinatario de un paquete se buscaba por teléfono y, si no, por NOMBRE tomando la primera coincidencia; con dos
personas del mismo nombre, el descuento/abono del contra entrega podía ir a la persona equivocada.

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Decisiones

- Orden: (1) teléfono del destinatario, solo si esa Persona tiene el mismo nombre (issue 101, teléfono "prestado");
  (2) el WhatsApp propio del destinatario (`Paquete.recipient_whatsapp`, issue 379) -- identidad exacta; (3) por
  nombre SOLO si hay una única Persona con ese nombre. Si el nombre es ambiguo: no se adivina -- el saldo no se
  muestra ni se registra para ese paquete (mejor que cargárselo a otra persona).
- Una sola función de dominio (`paquete_service.persona_destinataria`) para Recibir, Entregar y `/consultar` (antes
  duplicada en `packages.py` y `search.py`), y la misma regla en la versión por lotes de `/paquetes`.
- Limpieza: la documentación del modelo de saldo ya no dice que el saldo se usa entre residentes del mismo apartamento
  (se quitó a pedido del cliente), y se borran las dos funciones de ese selector que nadie usa.

## Verificación

- `tests/web/test_saldo_destinatario_sin_adivinar.py` (4; 3 fallaban antes): con dos homónimos el pago al mensajero no
  se le carga a ninguno y la caja no aparece; con nombre único sí; un destinatario solo-WhatsApp con nombre repetido
  se resuelve por su WhatsApp.
- Borradas `personas_con_historial_en_apartamento`/`_por_apartamentos` (sin uso desde que se quitó el selector) y sus
  3 pruebas de dominio, a propósito. Docstring de `MovimientoSaldoContraEntrega` corregido.
- Regresión: saldo, pago al mensajero, ajuste al entregar, `/paquetes`, `/consultar`, primera entrega (346) en verde.
- BD dev: 3 nombres repetidos y 3 paquetes abiertos con esos nombres. FJ4T y P5SJ se resuelven por teléfono (sin
  cambio); Y5U8 ("TEST 3", sin teléfono, con homónimo) antes podía caer en cualquiera de los dos y ahora se resuelve
  por su WhatsApp. Ninguno queda sin resolver.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar en vivo (localhost)". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
