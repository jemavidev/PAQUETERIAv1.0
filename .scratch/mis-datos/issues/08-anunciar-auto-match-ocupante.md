# 08 — `/anunciar` (público): auto-match contra el roster del apartamento + congelar el teléfono correcto

**What to build:** `/anunciar` NO cambia visualmente (sigue siendo teléfono + nombre en texto libre, sin mostrar ninguna lista de residentes — privacidad de una vista pública). La resolución nueva es enteramente privada/server-side: al recibir el envío, se busca la Persona por el teléfono escrito; si existe y tiene un Ocupante activo (Apartamento resuelto), se compara el nombre escrito contra **todo el roster de Ocupantes activos de ESE apartamento** (no solo el nombre propio del dueño del teléfono). Si coincide exactamente con algún Ocupante del roster, el paquete queda anunciado a nombre de ese Ocupante automáticamente — sin pasar por staff. El teléfono de notificación que se congela en el Paquete (snapshot inmutable, ADR-0001) es: el teléfono PROPIO del Ocupante si lo tiene EN ESE MOMENTO; si no, el teléfono del PRINCIPAL activo de ese Apartamento EN ESE MOMENTO. Si el nombre no coincide con nadie del roster (o el teléfono no resuelve a ningún Apartamento), cae al comportamiento actual (`Destinatario.declarado_por_cliente`, self-announce) — la ambigüedad la resuelve el staff después (ticket 09), nunca en el momento público de anunciar.

**Blocked by:** 03

**Status:** done

- [x] Anunciar con el teléfono del principal + su propio nombre funciona exactamente igual que hoy (sin regresión).
- [x] Anunciar con el teléfono del principal + el nombre de un Ocupante conocido de su mismo Apartamento resuelve automáticamente a ese Ocupante, sin pedir nada adicional ni pasar por staff.
- [x] El `recipient_phone` congelado en el Paquete es el del Ocupante si tiene teléfono propio en ese momento, o si no, el del principal activo del Apartamento en ese momento.
- [x] Anunciar con un teléfono+nombre que no coincide con ningún Ocupante del apartamento resuelto (o sin apartamento resuelto) cae al comportamiento actual, sin romper nada existente.
- [x] La vista pública `/anunciar` no cambia visualmente ni expone ninguna lista de nombres/candidatos (cero cambios en la ruta/plantilla de `/anunciar` — todo el trabajo fue en `paquete_service.announce`).
- [x] Tests cubren: match exacto contra el roster; match contra el propio nombre del anunciante (caso ya existente); Ocupante sin teléfono usa el del principal; Ocupante con teléfono propio lo usa a él; no-match cae al comportamiento de siempre; sin apartamento resuelto.

## Implementación

- `paquete_service.py`: `_resolver_ocupante_por_nombre` (busca en el roster activo del apartamento del anunciante) + `_telefono_notificacion_ocupante` (propio si tiene, si no el del principal), enganchados solo en la rama `DECLARADO_POR_CLIENTE` de `announce()`.
- 5 tests nuevos en `test_announce_paquete.py`. Suite completa: 504 passed, sin regresiones en ningún test existente de `/anunciar`, `/announce`, ni notificaciones.
