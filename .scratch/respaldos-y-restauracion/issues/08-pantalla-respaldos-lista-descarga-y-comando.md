# 08 — Pantalla "Respaldos": lista, descarga y comando de restauración

**What to build:** una pantalla "Respaldos" en `/administracion`, solo para ADMIN, en el menú de cuenta dentro de
"Datos". Muestra el estado del último respaldo, la lista de respaldos disponibles (fecha, tipo, tamaño, estado), deja
descargar cualquiera como `.zip` con sus cuatro archivos, y explica los pasos de restauración con el comando exacto
listo para copiar para el respaldo elegido.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] Operador → 403; sin sesión → login; enlace en "Datos" solo para ADMIN.
- [ ] Lista con fecha, tipo, tamaño y estado; estado del último respaldo visible arriba.
- [ ] Descarga `.zip` con los 4 archivos, transmitida por partes (sin armarla entera en memoria).
- [ ] Pasos de restauración y comando `restaurar.sh` exacto para el respaldo elegido.
- [ ] Pruebas HTTP: acceso por rol, lista, cabeceras y contenido del `.zip`, comando mostrado.
