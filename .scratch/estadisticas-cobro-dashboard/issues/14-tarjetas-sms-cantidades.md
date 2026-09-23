# 14 — Tarjetas de SMS: cantidades (Panorama + Periodo)

**What to build:** con el registro ya llenándose (11, 12), la tarjeta "SMS enviados por AWS" aparece en
Panorama (Hoy | Semana | Mes) y las tarjetas de cantidad de SMS aparecen en la categoría "SMS del
periodo" de Periodo seleccionado — solo cantidades todavía, el costo es el ticket 15.

**Blocked by:** 02, 11, 12

**Status:** ready-for-agent

- [ ] Panorama → "SMS enviados por AWS": cuenta, para Hoy/Semana/Mes, los mensajes del registro cuyo
      proveedor fue AWS SNS (avisos + códigos de acceso juntos) — no cambia con los filtros de la barra.
- [ ] Periodo → "SMS enviados por AWS": mismo conteo pero acotado al periodo seleccionado, con el
      desglose "X avisos · Y códigos de acceso".
- [ ] Periodo → "SMS fallidos": cuenta los mensajes del periodo que no entregó ningún proveedor.
- [ ] Un mensaje enviado por AWS tras fallar antes por LIWA (o viceversa) cuenta para el proveedor que
      SÍ lo entregó, no para el primero de la cadena que se intentó.
- [ ] Ambas tarjetas (Panorama y Periodo) muestran, en letra pequeña, desde qué fecha existe registro
      (la fecha del primer envío registrado) — para dejar claro que no es un histórico completo.
- [ ] Sin ningún envío registrado todavía, las tarjetas muestran 0 con esa misma aclaración, sin error.
- [ ] Matriz de "no aplica" en Periodo: ni Tipo ni Cobrado/Anulado acotan ninguna tarjeta de SMS (los
      envíos no tienen Tipo de paquete ni estado de cobro) — todas se atenúan con ambas notas cuando
      cualquiera de los dos filtros está activo.
