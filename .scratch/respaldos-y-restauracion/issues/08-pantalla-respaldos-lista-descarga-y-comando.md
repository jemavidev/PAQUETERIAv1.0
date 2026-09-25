# 08 — Pantalla "Respaldos": lista, descarga y comando de restauración

**What to build:** una pantalla "Respaldos" en `/administracion`, solo para ADMIN, en el menú de cuenta dentro de
"Datos". Muestra el estado del último respaldo, la lista de respaldos disponibles (fecha, tipo, tamaño, estado), deja
descargar cualquiera como `.zip` con sus cuatro archivos, y explica los pasos de restauración con el comando exacto
listo para copiar para el respaldo elegido.

**Blocked by:** 03

**Status:** done

- [x] Operador → 403; sin sesión → login; enlace en "Datos" solo para ADMIN.
- [x] Lista con fecha, tipo, tamaño y estado; estado del último respaldo visible arriba.
- [x] Descarga `.zip` con los 4 archivos, transmitida por partes (sin armarla entera en memoria).
- [x] Pasos de restauración y comando `restaurar.sh` exacto para el respaldo elegido.
- [x] Pruebas HTTP: acceso por rol, lista, cabeceras y contenido del `.zip`, comando mostrado.

## Comments

**2026-09-25 (PaqueteX `b558516`):** en test con un admin temporal: lista con estado S3 por respaldo ("En S3: diario /
puntual"), descarga `.zip` (2,3 MB, 4 archivos, huellas verificadas en otra máquina), comando `restaurar.sh` listo.
Solo se descargan los del disco: la llave del servidor no puede leer S3 (decisión 2); los anteriores se bajan de S3
con la cuenta de AWS de Jesús -- la pantalla lo dice.
