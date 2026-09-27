# 413 — Activar la compresión de respuestas en test.papyrus.com.co

**Pedido original (Jesús, 2026-09-26):** "activa la compresión en el servidor de test, en caso que hagas esto para que
serviria".

**Status:** implementado, desplegando a test (`3ea732f`)

## Alcance

- Hallazgo del 412: test responde sin `Content-Encoding`; `/paquetes?estado=ANUNCIADO` viaja como 1,6 MB de HTML.
- Se activa en Caddy (`encode zstd gzip`, repo de despliegue `jemavidev/PaqueteX`), no en la app: Caddy por defecto
  solo comprime tipos de texto (HTML, CSS, JS, JSON, SVG) y deja pasar tal cual fotos JPEG y descargas `.zip`.
- El CI de despliegue solo reinicia `app`; se le agrega reiniciar `caddy` cuando cambia el `Caddyfile` (montado como
  archivo suelto: `git reset` le cambia el inodo y un `caddy reload` seguiría leyendo el viejo).

## Implementado (2026-09-26)

- Primera prueba local (caddy:2-alpine delante de :8010): CSS/JS se comprimían, pero **/paquetes no** -- su
  `StreamingResponse` emite pedazos chicos y Caddy, sin largo conocido, decide con el primero (< 512 B) no comprimir.
- Arreglo en `packages.py`: `_en_bloques` agrupa el stream en bloques de >= 16 KB. Resultado local:
  `/paquetes?estado=ANUNCIADO` 1.493.422 B -> 256.334 B (gzip) / 99.230 B (zstd); `/paquetes` 644.472 -> 63.622 B
  (zstd); contenido idéntico tras descomprimir; primer byte sigue llegando al instante (streaming intacto).
- 596 pruebas de /paquetes en verde. Deploy repo: `Caddyfile` + `ci.yml` (restart de caddy si cambia el Caddyfile).
