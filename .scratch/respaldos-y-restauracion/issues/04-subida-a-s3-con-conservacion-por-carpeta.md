# 04 — Subida a S3 con conservación por carpeta

**What to build:** cada respaldo se sube al bucket `paquetex-respaldos` (cuenta `172460160630`) bajo la carpeta del
dominio del servidor, en `diario/`, `mensual/` (copia del día 1), `anual/` (1 de enero) o `puntual/` según fecha y
motivo. Se crean en AWS el bucket (privado, cifrado por defecto), sus reglas de ciclo de vida y la llave de solo subida
de test, definidos como archivos en el repo sin secretos; la llave se instala directo en el `.env` de test por SSH sin
mostrarse.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] Políticas, reglas de ciclo de vida y script de creación versionados en el repo, sin ningún secreto.
- [ ] Bucket creado: privado, cifrado por defecto, reglas `diario/` y `puntual/` 30 días, `mensual/` 365 días,
      `anual/` sin expiración.
- [ ] Llave de test: solo puede subir bajo `test.papyrus.com.co/`; verificado en vivo que NO puede leer, listar ni
      borrar, ni escribir en la carpeta de otro dominio.
- [ ] Un respaldo del día 1 queda en `diario/` y `mensual/`; el del 1 de enero además en `anual/`; uno "antes de
      deploy" o "a pedido" en `puntual/`.
- [ ] Si la subida falla, el respaldo local se conserva y el error queda registrado (el aviso por correo es del 05).
- [ ] Pruebas con el destino S3 falso: carpeta correcta según fecha y motivo, nombres únicos (sin sobrescribir).
