# 144 — Letras grises más oscuras en todo el sistema (contraste)

**Pedido original (cliente):** "posibilidades de que las letras sean un poco más oscuras,
posiblemente negras, las que actualmente son grises... es que el contraste en uno de los
equipos que manejamos solo se vería mejor con letras más oscuras" → confirmó "aplícaselo a
todo" tras proponerle subir un escalón el tono (no saltar directo a negro, para no aplanar la
jerarquía visual label/dato).

**Status:** implementado

## Implementación

No existe un token central para estos grises (`slate`/`gray` en `tailwind.config.js` son la
paleta estándar de Tailwind, sin override — solo los colores `papyrus-*` están personalizados)
así que el cambio se aplicó como reemplazo de clase, un escalón más oscuro, en las 39 plantillas
que las usaban:

- `text-slate-400` → `text-slate-600`
- `text-slate-500` → `text-slate-700`
- `text-slate-600` → `text-slate-800`
- `text-gray-400` → `text-gray-600`
- `text-gray-500` → `text-gray-700`
- `text-gray-600` → `text-gray-800`

227 reemplazos (script Python con regex, sustitución simultánea para no encadenar shifts).

**Excluido a propósito** (no son "letras de contenido", son estados con función propia):
`placeholder:text-slate-400` (3 casos, hint de campo vacío) y `disabled:text-gray-400` (1 caso,
señal visual de "no interactuable" en `_botones.html`) — oscurecerlos los volvería
indistinguibles del texto real/activo.

`npm run build:css` (agregó `hover:text-slate-800`, no existía antes en el CSS compilado) +
`tailwind.css?v=61`.

## Verificación

- Playwright: color computado de un elemento con `text-slate-700` en `/paquetes` y
  `/administracion/personal` → `rgb(51, 65, 85)`, confirmado.
- Test suite completo: pendiente de resultado final (corriendo en background al momento de
  este registro).
- Pendiente: deploy a test.papyrus.com.co + confirmación del cliente en vivo, en particular en
  el equipo que reportó el problema de contraste.
