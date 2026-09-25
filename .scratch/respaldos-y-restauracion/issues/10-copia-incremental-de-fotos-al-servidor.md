# 10 — Copia incremental de fotos al servidor

**What to build:** en la pantalla "Respaldos", un botón que copia las fotos de S3 a una carpeta del servidor fuera del
proyecto, incremental (la primera vez todas, después solo las que falten), con la misma estructura de carpetas de S3,
en segundo plano y mostrando el avance ("copiando 1.234 de 7.511"). La llave de fotos del servidor gana permiso de leer
y listar solo el bucket/prefijo de fotos. Reusa el mecanismo de segundo plano del 09.

**Blocked by:** 09

**Status:** ready-for-agent

- [ ] Permiso de lectura y listado agregado solo sobre las fotos; definido en el repo y aplicado en la cuenta.
- [ ] Primera corrida copia todo; la siguiente copia solo lo nuevo y nunca borra nada local.
- [ ] Avance visible y persistente; se puede cerrar la pantalla mientras corre.
- [ ] Pruebas con el origen de fotos falso: primera copia completa, segunda incremental, estructura de carpetas.
- [ ] Verificado en vivo en test con las fotos reales (medir tamaño y tiempo de la primera copia).
