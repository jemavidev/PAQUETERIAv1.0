# 385 — `/anunciar`: límites por teléfono con mensaje amigable

**Pedido original (Jesús):** "con un límite por cliente (número de teléfono), después de un número de anuncios, sugerir activar la recepción automática desde mis datos o solicitando al personal de staff que lo activen ... mensaje amigable"; "la recepción automática ya existe de forma de flag" (hallazgo 3).
Respuesta de Jesús a la auditoría funcional (`.scratch/auditoria-funcional-2026-09-23/reporte.md`), 2026-09-23 — "soluciona estas cositas"; todo en localhost, el servidor de test se habla después.

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Decisiones

- Anuncios pendientes por teléfono: máximo 3 sin historial (nunca se le recibió un paquete), 5 con historial;
  máximo 5 anuncios por día por teléfono.
- SMS de "Anunciado": máximo 1 por teléfono por día; los demás anuncios se registran igual, sin SMS.
- Al llegar al límite, mensaje amigable que invita a activar "Autorizo a Papyrus para recibir todos los paquetes a mi
  nombre" (`autoriza_recepcion_automatica`) en Mis datos, o a pedírselo a portería; si ya la tiene activa, le dice que
  no necesita anunciar.
- La vista sigue revelando si un teléfono ya es cliente (hallazgo 11): se deja así por decisión de Jesús.

## Verificación

- `tests/web/test_anunciar_limites_por_telefono.py` (6) + 3 de `test_announce.py` reescritas a propósito (fijaban el tope de 10): 3 pendientes sin historial, 5 con historial, 5 por día, un SMS por teléfono por día, mensaje amigable con la recepción automática (y variante si ya la tiene activa).

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar en vivo (localhost)". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
