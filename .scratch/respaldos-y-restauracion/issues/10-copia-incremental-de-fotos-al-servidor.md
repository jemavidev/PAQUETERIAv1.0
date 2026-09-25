# 10 — Copia incremental de fotos al servidor

**What to build:** en la pantalla "Respaldos", un botón que copia las fotos de S3 a una carpeta del servidor fuera del
proyecto, incremental (la primera vez todas, después solo las que falten), con la misma estructura de carpetas de S3,
en segundo plano y mostrando el avance ("copiando 1.234 de 7.511"). La llave de fotos del servidor gana permiso de leer
y listar solo el bucket/prefijo de fotos. Reusa el mecanismo de segundo plano del 09.

**Blocked by:** 09

**Status:** done

- [x] Permiso de lectura y listado agregado solo sobre las fotos; definido en el repo y aplicado en la cuenta.
- [x] Primera corrida copia todo; la siguiente copia solo lo nuevo y nunca borra nada local.
- [x] Avance visible y persistente; se puede cerrar la pantalla mientras corre.
- [x] Pruebas con el origen de fotos falso: primera copia completa, segunda incremental, estructura de carpetas.
- [x] Verificado en vivo en test con las fotos reales (medir tamaño y tiempo de la primera copia).

## Comments

**2026-09-25 (PaqueteX `b558516`):** en test desde la pantalla: primera copia 7.561 fotos (550 MB, ~15 min, avance
visible "Copiando fotos: 150 de 7.561"...), segunda copia "0 fotos nuevas copiadas, 7561 ya estaban". Disco al 25 %.
