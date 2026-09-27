# 01 — Recibir captura la Posición (todavía opcional)

**What to build:** al Recibir un Paquete, el Operador ve al final del modal (justo antes del botón Recibir) una grilla de 14 botones que reproduce el estante físico — fila 7 arriba, fila 1 abajo; cada fila `[x2 | x1]` (72|71 … 12|11) — y elige la Posición con un toque (solo selecciona, no envía). Recibir persiste la Posición elegida. Aplica en los tres lugares que reutilizan el modal (/paquetes, /announce, /consultar). En esta rebanada la Posición es todavía opcional; un código fuera de los 14 se rechaza sin efecto. Spec: `../spec.md`.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] Término **Posición** agregado a `CONTEXT.md` (11…72, fila + lado, 1 = derecha, 2 = izquierda).
- [x] Un módulo de dominio es dueño del conjunto fijo de Posiciones válidas, su validación y el orden de la grilla.
- [x] Columna nullable en Paquete con `CHECK` de BD restringida a los 14 códigos; migración Alembic sin backfill.
- [x] `receive()` de dominio acepta `posicion`, la valida antes de mutar (inválida → excepción, paquete intacto) y la persiste; sin ella queda NULL.
- [x] El endpoint de recibir acepta el campo `posicion` y lo pasa al dominio; un código inválido se rechaza sin efectos colaterales.
- [x] El modal Recibir muestra la grilla en orden de estante, antes del botón Recibir, en /paquetes, /announce y /consultar.
