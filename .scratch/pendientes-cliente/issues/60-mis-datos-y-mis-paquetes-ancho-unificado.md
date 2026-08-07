# 60 — `/mis-datos` y `/mis-paquetes`: unificar ancho/alineación del contenedor

**Pedido original (cliente):** "veo que el contenido de estas 2 vistas no
se ven acorde, una es mas ancha que la otra y esta alineada de forma
diferente, puedes analizar esto y corregirlo, al cambiar entre una y otra
esto no se deberia notar ya que debe ser con las mismas clases o
similares."

**Status:** verificado (el cliente confirmó "Casi perfecto, estas
mejorando" en `test.papyrus.com.co`)

## Análisis

`/mis-datos` usaba `max-w-lg lg:max-w-2xl mx-auto px-4 py-8` (512px mobile
/ 672px desktop). `/mis-paquetes` usaba `max-w-[480px] lg:max-w-[720px]
mx-auto px-4 py-6` (480px / 720px) — ancho distinto en las 2 resoluciones
y menos padding vertical. Mismo `mx-auto` en las dos, así que la
diferencia de ancho se percibía como "alineado distinto": un contenedor
más angosto centrado en la misma pantalla deja más margen a los lados, el
contenido arranca más lejos del borde.

## Corrección

`/mis-paquetes` pasa a usar exactamente las mismas clases que `/mis-datos`:
`max-w-lg lg:max-w-2xl mx-auto px-4 py-8`.

Alcance: solo el contenedor exterior (ancho/padding/centrado) -- no se
tocó el estilo de las tarjetas de paquete (`rounded-lg shadow-sm` en
`/mis-paquetes` vs `rounded-2xl shadow` en las tarjetas de `/mis-datos`),
ya que el pedido fue específicamente sobre ancho y alineación, no sobre
esquinas/sombra de las tarjetas.

## Verificación

- Sintaxis Jinja verificada con `Environment.parse()`.
- `tests/web/test_mis_paquetes.py` + `tests/web/test_layout.py`: 41/41.
- Suite completa (`tests/data_model tests/web`): 635/635, sin regresiones.
- Sin clases Tailwind nuevas (`max-w-lg`/`max-w-2xl`/`py-8` ya existían) --
  no hizo falta recompilar `tailwind.css`.
- Pendiente: confirmar en `test.papyrus.com.co` que las 2 vistas se ven
  igual de anchas y alineadas al cambiar entre una y otra.
