# 373 — Menú de cuenta: ítem "Este equipo tiene lector" → "Lector"

**Pedido original (Jesús):** "ahora necesito que cambies esto 'Este equipo tiene lector' por 'Lector'".

**Status:** implementado, pendiente confirmar visualmente

## Contexto

`CODE/src/app/web/templates/base.html` -- el ítem del menú de cuenta que activa el modo lector
(`.scratch/captura-guia-lector-camara`, ticket 10) mostraba el texto completo "Este equipo tiene
lector" junto al ícono de código de barras y el estado ("Activado"/"Desactivado" a la derecha).

## Decisiones

- Solo cambia el texto visible del `<span>` del ítem, a "Lector". El estado a la derecha
  ("Activado"/"Desactivado") no cambia, ni el ícono, ni el mecanismo (localStorage por equipo,
  `data-modo-lector`, `aria-checked`).
- Se actualizan también los lugares que citan el texto anterior como parte de instrucciones o
  aserciones vigentes: el manual del Operador (`docs/manual-usuario/02-staff-operador.md`),
  `CONTEXT.md` (glosario, "Modo lector"), los tests que verifican ese texto en la página
  (`tests/web/test_captura_guia.py`), el docstring de `tests/browser/_ayudantes.py` y el
  comentario de `icons.py`.
- No se tocan los registros históricos de la feature (`.scratch/captura-guia-lector-camara/
  decisiones-grilling.md`, `spec.md`, `issues/10-*.md`, `issues/12-*.md`, `issues/14-*.md`):
  documentan lo decidido/construido en su momento, con el texto que existía entonces.

## Verificación

- `tests/web/test_captura_guia.py`: las 3 aserciones que verificaban el texto anterior por
  substring pasan a verificar "Lector".
- Suite web y de navegador (seam `browser`) corridas tras el cambio, sin regresiones.
