# 271 — `/residentes`: "Mudar residente de apartamento" y "Recibir paquetes sin autorización" pasan a toggle switch

**Pedido original (cliente):** "Necesito que estas 2 opciones 'Mudar
residente de apartamento y Recibir paquetes sin autorización' tengan
mejor opción de toggle."

**Status:** implementado

## Verificación

Suite `test_customers_manage.py`: 151 passed (incluye
`test_ficha_muestra_el_checkbox_de_recepcion_automatica_marcado`, que
asertaba el formato exacto `name="..." checked` -- el macro nuevo lo
preserva). `npm run build:css` corrido y committeado (ambas copias,
legacy + rebuild), `?v=65` → `?v=66`. Verificado en vivo: los 2
toggles renderizan (`peer sr-only` x2), y la regla CSS
`peer-checked:bg-blue-800` se sirve realmente desde
`/static/css/tailwind.css?v=66`.

Seguimiento (`/mis-datos`): suite `test_customer_verify.py` +
`test_customers_manage.py` completa (incluye
`test_autoriza_recepcion_automatica_desactivado_por_default`, que
verifica el formato exacto): 217 passed. Verificado en vivo (login
real por OTP): el toggle renderiza y el link "Términos y condiciones"
sigue intacto adentro.

## Alcance

Nuevo macro `components/_inputs.html::toggle(label, name, checked=False,
id=none, extra_attrs='')` -- switch deslizante clásico (pista + thumb
circular, `peer`/`peer-checked`/pseudo-elemento `after:`), mismo azul
primario (`bg-blue-800`) y mismo anillo de foco (`focus-visible:ring-2
ring-blue-300`) que el resto del design system. Reemplaza el `<input
type="checkbox">` nativo en:

- `customers_manage/detail.html` línea ~106 -- "Recibir paquetes sin
  autorización" (tab Datos).
- `customers_manage/detail.html` (issue 270) -- "Mudar residente de
  apartamento" (tab Dirección).

`customer/verify.html` tiene el MISMO checkbox "Recibir paquetes sin
autorización" (línea 88, `/mis-datos`) -- el pedido fue puntual sobre
lo que el cliente tenía abierto (`/residentes`), no se toca a menos
que lo pida también.

## Seguimiento (mismo día): también en /mis-datos

El cliente pidió aplicarlo "donde se requiera" -- el checkbox gemelo
de `/mis-datos` tiene contenido más rico (incluye el link a "Términos
y condiciones", issue 209/210), así que el macro `toggle()` se
extendió para aceptar un bloque `{% call %}...{% endcall %}` (mismo
patrón que ya usa `modal_confirmacion`, `caller is defined`) en vez de
solo texto plano vía el argumento `label`. También cambia `items-center`
→ `items-start` en el `<label>` -- necesario para que un texto que
envuelve a 2+ líneas alinee el switch con la primera línea, no con el
centro vertical de todo el bloque (no afecta los casos de una sola
línea de /residentes).

Como se agregan clases Tailwind nuevas (`peer`, pseudo-elemento
`after:` con `content-['']`), hace falta recompilar `tailwind.css`
localmente y commitear el archivo (no solo subir `?v=`) -- ver memoria
`paquetex-tailwind-build.md`.
