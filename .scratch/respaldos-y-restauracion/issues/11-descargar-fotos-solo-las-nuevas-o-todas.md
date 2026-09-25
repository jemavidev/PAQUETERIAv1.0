# 11 — Descargar fotos: "solo las nuevas" o "todas"

**What to build:** con las fotos copiadas al servidor, la pantalla ofrece "Descargar solo las nuevas" (desde la última
descarga, registrada por sistema) y "Descargar todas", como `.zip` transmitido por partes con la misma estructura de
carpetas de S3. Muestra la fecha de la última descarga y cuántas fotos nuevas hay y cuánto pesan.

**Blocked by:** 10

**Status:** ready-for-agent

- [ ] "Solo las nuevas" incluye exactamente las fotos creadas desde la última descarga y actualiza la marca.
- [ ] "Todas" siempre disponible, no depende de la marca.
- [ ] Muestra "N fotos nuevas (≈ X MB) desde el <fecha>".
- [ ] El `.zip` se transmite por partes: una descarga de varios GB no agota la memoria del servidor de 1 GB.
- [ ] Pruebas HTTP: nuevas vs todas, marca por sistema, contenido y estructura del `.zip`.
