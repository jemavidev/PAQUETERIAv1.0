# 11 — Registro de envíos de SMS: avisos de paquete, con el proveedor que entregó

**What to build:** cada SMS de aviso de estado de un paquete (Anunciado/Recibido/Entregado/Cancelado)
que sale por un proveedor SMS real (AWS SNS, LIWA o Twilio) queda anotado en un registro nuevo, junto con
CUÁL de esos proveedores lo entregó de verdad — dato que hoy no existe en ningún lado (los remitentes
solo devuelven éxito o excepción). Sin este ticket, ninguna tarjeta de SMS del tablero (14, 15, 16) es
posible.

**Blocked by:** None — can start immediately.

**Status:** implementado (cerrado en la revisión del 2026-09-26; evidencia: `registro_sms_service.py` + migración 0055)

- [ ] Existe un registro (tabla nueva, append-only, con su migración Alembic y el ORM alineado con ella)
      que anota, por cada intento de envío real: el momento, el tipo (por ahora solo "aviso de paquete"),
      el evento del paquete, a qué paquete corresponde, qué proveedor lo entregó, y si fue exitoso o
      falló en todos.
- [ ] El registro NO guarda el texto del mensaje ni el teléfono completo del destinatario.
- [ ] Cada uno de los tres remitentes SMS reales (AWS SNS, LIWA, Twilio) se identifica a sí mismo como
      proveedor cuando entrega un mensaje.
- [ ] Cuando la cadena de failover prueba varios proveedores en orden, el registro anota el proveedor que
      REALMENTE entregó (no el primero de la lista) — si AWS falla y LIWA lo entrega, la fila dice LIWA,
      no AWS.
- [ ] Si los tres proveedores configurados fallan, el registro anota una fila de tipo "fallido" (sin
      proveedor), una sola vez por mensaje — nunca una fila por cada intento fallido de la cadena.
- [ ] El remitente de consola/desarrollo (el que usa el ambiente local y los tests) NO registra nada.
- [ ] Registrar es best-effort: si anotar la fila falla por cualquier motivo, el envío del SMS y la
      transición del paquete NO se ven afectados — se prueba explícitamente forzando un fallo al
      registrar y confirmando que el aviso salió igual.
- [ ] El servicio de dominio del registro expone contar envíos por proveedor, tipo y rango de fechas, y
      obtener la fecha del primer registro que exista.
- [ ] Pruebas con proveedores falsos (no se golpea AWS/LIWA/Twilio reales) que cubren: éxito directo,
      éxito tras failover, fallo total, y el remitente de consola sin registrar.
