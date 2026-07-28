# Spec — Plantilla Anunciado dividida Cliente/Staff (Grupo 19, Ronda 2)

**Fuente:** `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 19.

## Qué cambia

`PlantillaNotificacion` ya tenía una columna `motivo` genérica (hasta ahora
solo usada por `CANCELADO` para sus 4 motivos). Se reutiliza esa misma
columna como llave de sub-variante para `ANUNCIADO`:

- `ORIGEN_ANUNCIO_CLIENTE` ("CLIENTE") — el residente anunció él mismo desde
  `/anunciar`.
- `ORIGEN_ANUNCIO_STAFF` ("STAFF") — el staff anunció a su nombre desde
  `/announce` (Grupo 6, Ronda 1).

`notificacion_service.origen_anuncio(paquete)` resuelve cuál de las dos
aplica mirando `paquete.announced_by_usuario_id` — el mismo dato que ya usa
la auditoría de actor del Grupo 11 (Ronda 2), sin ningún campo nuevo.

`construir_mensaje` y `plantilla_por_defecto` ahora ambos requieren `motivo`
para `ANUNCIADO` (antes no aplicaba). `/administracion/notificaciones` gana
2 filas ("ANUNCIADO · Cliente" / "ANUNCIADO · Staff") en vez de 1 — la
plantilla ya renderizaba el label genéricamente vía `fila.motivo`, sin
necesitar cambios de template.

## Por qué

Instrucción explícita del usuario: "así mismo como existen motivos de
cancelación, debería existir 2 tipos de anuncios... con su mensaje para
cada caso" — mismo patrón exacto que CANCELADO, cero esquema nuevo.

## Fuera de alcance

- No se tocan RECIBIDO/ENTREGADO (siguen sin motivo, sin cambios).
