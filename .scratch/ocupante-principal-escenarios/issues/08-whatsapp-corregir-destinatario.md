# 08 — WhatsApp para residentes secundarios: Corregir destinatario

**What to build:** en `/paquetes` → Corregir destinatario → "nuevo ocupante", el campo "Teléfono" pasa a un input único "Teléfono o WhatsApp" autoclasificado; el mensaje de error genérico actual ("Escribí el nombre del nuevo ocupante.", que hoy cubre tanto "sin apartamento en el snapshot" como "falta el nombre") se separa en dos mensajes específicos.

**Blocked by:** 01 (clasificador compartido), 06 (reusa las funciones de dominio de WhatsApp).

**Status:** ready-for-agent

- [ ] El formulario "nuevo ocupante" de Corregir destinatario usa el input único autoclasificado.
- [ ] Mensaje distinto para "este paquete no tiene apartamento resuelto en su snapshot" vs. "falta el nombre del nuevo residente".
- [ ] Tests en `test_packages.py` cubriendo: nuevo ocupante con WhatsApp, y los dos mensajes de error por separado.
