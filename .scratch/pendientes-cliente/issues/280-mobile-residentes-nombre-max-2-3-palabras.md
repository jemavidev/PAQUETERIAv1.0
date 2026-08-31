# 280 — Seguimiento a [[279]]: nombre en mobile acotado a 2-3 palabras (no "…")

**Pedido original (cliente):** "mucho mejor, se ve espectacular, creemos
reglas ahora, cada vez que muestres un nombre de cliente aqui en esta
vista de residente, solo permite maximo 2 o 3 palabras segun corresponda
para que no se sobre pase en el tamaño del nombre a mostrar, esto con la
idea de que no exeda lo que se quiere mostar, no vas a cambiar el
contenido del nombre del cliente en la base de datos, solamente el como
se muestra en esta vista y en version dispositivo movil y si el tamaño
alcanza o no"

**Status:** verificado (desplegado y confirmado en test.papyrus.com.co)

## Alcance

Solo mobile, solo cómo se MUESTRA el nombre en la tabla plana de
`/residentes` (columna Nombre) -- el valor real en base de datos
(`Persona.nombre`) no se toca en ningún punto de este cambio.

Reemplaza el truncado por caracteres retirado en [[279]] (que el
cliente pidió quitar por cortar a mitad de palabra) con una regla
distinta: máximo 3 palabras completas, o 2 si 3 palabras siguen siendo
demasiado largas. Nuevo helper `_nombre_mobile(nombre)` en
`customers_manage.py` (mismo patrón que `_etiqueta_torre_apto`, pasado
al contexto Jinja):

- Nombre de 1 o 2 palabras: se muestra completo (ya cumple el máximo).
- 3+ palabras: si las primeras 3 juntas miden ≤20 caracteres, se
  muestran esas 3; si no, solo las primeras 2.

El umbral de 20 caracteres es una aproximación razonable al ancho real
disponible en mobile (calibrado contra las medidas de [[277]]/[[278]],
~85-180px según el viewport, que a este tamaño de fuente ronda los
15-25 caracteres) -- no hay forma de medir el ancho real en píxeles
desde el server (Jinja), así que es una heurística por caracteres, no
una medición exacta.

Reinstaura el patrón de 2 versiones (mobile/desktop) que ya usan Torre
y Apartamento desde [[277]] -- en mobile se muestra el nombre acotado,
desde `sm:` el nombre completo de siempre, sin cambios ahí. Sin
`truncate`/"…" en ningún lado -- el cliente fue explícito en [[279]]
sobre no querer cortes de caracteres a mitad de palabra.

## Verificación

Suite completa (`pytest tests/web/test_customers_manage.py`) + nuevo
test unitario para `_nombre_mobile` cubriendo los 3 casos (≤2 palabras,
3 palabras corta, 3+ palabras larga). Verificado en vivo con los mismos
anchos de referencia de [[277]]/[[278]] (iframe same-origin en dev
local). Desktop sin cambios.
