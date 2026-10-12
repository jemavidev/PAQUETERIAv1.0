# 06 — Reglas de quién puede recibir SMS

**What to build:** El botón SMS respeta las mismas reglas que los avisos automáticos. Si no aplica, queda apagado con el motivo visible
y el WhatsApp sigue disponible. Las reglas se revisan al dibujar la lista y también en el POST de envío. Los clientes
que solo tienen usuario de WhatsApp (sin teléfono) también aparecen en la lista, con el SMS apagado.

Ver spec: Implementation Decisions (Regla del SMS, Quién es "el cliente") y User Stories 41-47.

**Blocked by:** 05 — Enviar SMS y "Último SMS"

**Status:** done (2026-10-11)

- [x] Motivos, en este orden de prioridad: "De baja" (baja administrativa), "Sin teléfono", "Notificaciones SMS desactivadas"
- [x] "Notificaciones SMS desactivadas" solo si el cliente APAGÓ A PROPÓSITO el SMS (preferencia guardada en falso) para el Estado de TODOS sus paquetes en la lista; los valores por defecto no bloquean (decisión de Jesús, 2026-10-11 -- antes decía `preferencia_activa`, que con el default de Recibido apagado dejaba sin SMS a casi todos)
- [x] Un POST de envío a un cliente no elegible se rechaza sin llamar al sender ni registrar envío
- [x] Los clientes solo-WhatsApp aparecen con "Sin teléfono" y el WhatsApp disponible, sin cambiar el comportamiento de los avisos automáticos
- [x] El bloqueo no agrega una regla nueva (igual que los avisos automáticos)
- [x] Pruebas por HTTP y, para la matriz de motivos, sobre el servicio de dominio
