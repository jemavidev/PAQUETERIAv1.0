# 11 — Descargar fotos: "solo las nuevas" o "todas"

**What to build:** con las fotos copiadas al servidor, la pantalla ofrece "Descargar solo las nuevas" (desde la última
descarga, registrada por sistema) y "Descargar todas", como `.zip` transmitido por partes con la misma estructura de
carpetas de S3. Muestra la fecha de la última descarga y cuántas fotos nuevas hay y cuánto pesan.

**Blocked by:** 10

**Status:** done

- [x] "Solo las nuevas" incluye exactamente las fotos creadas desde la última descarga y actualiza la marca.
- [x] "Todas" siempre disponible, no depende de la marca.
- [x] Muestra "N fotos nuevas (≈ X MB) desde el <fecha>".
- [x] El `.zip` se transmite por partes: una descarga de varios GB no agota la memoria del servidor de 1 GB.
- [x] Pruebas HTTP: nuevas vs todas, marca por sistema, contenido y estructura del `.zip`.

## Comments

**2026-09-25 (PaqueteX `b558516`):** en test: "Descargar todas" 562 MB, 7.561 fotos con la estructura de S3, zip íntegro,
sin problemas de memoria en el servidor de 1 GB. "Solo las nuevas": 1.ª = 7.519 (= fotos registradas en la base), 2.ª
= 0; la pantalla muestra "0 fotos nuevas desde el ..., la última descarga". "Todas" incluye además 42 archivos de S3
que no están registrados en el sistema.
