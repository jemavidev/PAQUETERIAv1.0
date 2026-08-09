# 71 — `/residentes`: acento de borde en vez de fondo completo para Residente Secundario

**Pedido original (cliente):** sobre el fondo rojizo completo probado en
[[69]] para distinguir Residentes Secundarios (fila de la lista + tabs de
la ficha), el cliente expresó duda ("OK, pero no sé"). Se le presentaron 4
alternativas vía pregunta directa; eligió **"Cambiar a un borde/acento de
color"** — una franja de color a la izquierda en vez de rellenar todo el
fondo.

**Status:** implementado

## Implementación

- `search.html`: la fila pasa de `bg-red-50 hover:bg-red-100` a
  `hover:bg-slate-50` (comportamiento normal) + `border-l-4
  border-l-red-400` condicional.
- `detail.html`: cada `tab-panel` pasa de `bg-red-50 rounded-2xl p-3` a
  `border-l-4 border-red-400 pl-3` condicional.
- Mismo `{% set es_secundario %}` de antes, solo cambia la clase aplicada.

## Verificación

- Sintaxis Jinja verificada con `Environment.parse()`.
- Verificación visual en navegador real (Playwright): acento visible y
  sutil en ambas vistas, sin errores de consola.
- Suite completa (`tests/data_model tests/web`): 689/689, sin
  regresiones. 3 tests actualizados para el nuevo marcador CSS
  (`border-l-4 border-red-400` / `border-l-4 border-l-red-400`).
- Tailwind recompilado y comiteado — `?v=36` → `?v=37`.
