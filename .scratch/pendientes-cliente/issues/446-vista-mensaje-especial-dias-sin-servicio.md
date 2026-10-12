# 446 — Vista de mensaje especial (fines de semana / días sin servicio)

**Pedido original (Jesús, 2026-10-11):** "Necesito una vista para notificaciones de un mensaje especial, por ejemplo
fines de semana, o mensajes especiales en los dias que no vamos a estar disponibles prestando el servicio de paquetes,
esto aplicara solamente para paquetes anunciados (menos de 5 dias desde su anuncio) y paquetes recibidos en general.
Clona lo que es la vista de /paquetes y realiza la propuesta para estos que esten en la lista para poder enviar un
mensaje de texto y mensaje por whatsapp por medio de un link (boton). El mensaje se podra editar en
/administracion/notificaciones."

**Status:** desglosado en 8 tickets en `.scratch/avisos-especiales/issues/` (2026-10-11); pendiente de implementar

## Decisiones (grilling, Jesús 2026-10-11)

1. **SMS por la cadena de proveedores existente** (AWS SNS primero), solo al presionar el botón, nunca automático.
2. **Una fila por cliente** (no por paquete), con sus paquetes resumidos.
3. **Último SMS solo informativo**: sin confirmación ni bloqueo de reenvío.
4. **Varios mensajes guardados** (nombre + texto), editables cuando haya información nueva.
5. **Último SMS por cliente**, sin importar cuál mensaje, mostrando el nombre del mensaje enviado.
6. **Solo cuenta el SMS**: el botón de WhatsApp es un enlace y no deja registro.
7. **Mismas reglas que los avisos automáticos**: de baja, notificaciones apagadas o sin teléfono → SMS apagado con el
   motivo visible; WhatsApp sigue disponible.
8. **Texto fijo con `{nombre}` y `{codigos}`** como únicas variables; vista previa con conteo de caracteres (160 = 1
   SMS).
9. **Solo Admin**, tanto la vista como la edición de los mensajes; entrada por el menú de cuenta.
10. **Anunciados de los últimos 5 días calendario** (hora de Colombia, hoy + 4 anteriores) y **todos los Recibidos**;
    nunca Entregados/Cancelados.
11. **Selector de mensaje arriba de la lista**, con vista previa; todos los botones usan el elegido.
12. **Envío sin recargar** ("Enviando…" → la fila muestra el nuevo último SMS); si falla, aviso rojo en la fila y no
    cuenta como último envío; cada envío queda en `registros_sms` (Dashboard).
13. **Mensajes administrados en `/administracion/notificaciones`** (sección "Mensajes especiales"): crear, editar,
    eliminar con confirmación, historial de cambios; **un solo texto** para SMS y WhatsApp.

Look de la lista: el de `/paquetes` escritorio (filas-tarjeta, issue 445), con búsqueda y filtro Anunciado/Recibido.
