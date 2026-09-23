# 360 — `/administracion/contactos-externos` mobile: usuario de WhatsApp en píldora bajo el nombre

**Pedido original (Jesús):** "Necesito que en la vista de
/administracion/contactos-externos, en la version mobil, permitas que el
usuario de whatsapp sea visible por medio de una pildora debajo del nombre,
en este caso quedaria por cada contacto 2 filas 'Nombre' al lado izquierdo,
'Contacto de whatsapp' debajo del nombre en la nueva fila, El 'numero de
telefono' al lado derecho."

**Status:** implementado (ronda 2), pendiente confirmar visualmente

## Contexto

En la tabla, la columna WhatsApp es `hidden sm:table-cell` -- en mobile
(`< sm`, 640px) solo se ven Nombre y Teléfono(s), y el usuario de WhatsApp no
se ve en ningún lado. Mismo patrón que `/residentes` (issues 277/278/281) y
`/paquetes` (341): lo que sale de la tabla en mobile baja a una píldora bajo
el nombre.

## Decisiones

- Corte `sm:hidden`, el mismo de la columna WhatsApp: nunca se ven a la vez la
  columna y la píldora, ni queda un rango sin ninguna de las dos.
- Una píldora por cada usuario de WhatsApp del contacto (puede tener varios).
  Sin WhatsApp no se dibuja nada (precedente: issue 345, sin píldora "apagada").
- Nombre y píldora en la celda izquierda, teléfono(s) en la derecha.

## Implementación

- Celda Nombre: nombre + `div.sm:hidden` con una píldora esmeralda (ícono de
  WhatsApp + usuario, `break-all`) por cada usuario del contacto.
- Celda y encabezado Teléfono(s): `text-right`/`align-top` solo bajo `sm`
  (pegado al borde derecho y alineado con la 1ra fila); desde `sm` como antes.
- `tailwind.css` recompilado (`npm run build:css`, ambas copias) y `?v=` de
  `base.html` 95 -> 96, por las clases nuevas de 357-360.

## Verificación

- 4 tests nuevos: píldora en la celda del nombre y no en la del teléfono; 2
  píldoras con 2 usuarios; ninguna sin WhatsApp; la columna de desktop sigue.
- Markup verificado en vivo en `localhost:8010`; falta el ojo en un viewport
  mobile real (no se hizo QA visual en navegador).

## Ronda 2

**Pedido (Jesús):** "las pildoras de whatsapp en la version mobil deben ser
similar a como se han venido utilizando en las diferentes vistas".
**Status de la ronda:** implementada

La ronda 1 dibujó la píldora más chica (`px-2.5 py-0.5 text-xs`) y con un
ícono. Las píldoras mobile de `/residentes` (277/278/281) y `/paquetes` (341)
comparten una receta: `inline-flex items-center bg-* text-* border rounded-full
px-3 py-1.5 text-sm font-semibold whitespace-nowrap`, solo texto (sin ícono;
el cliente pidió quitar el de Apartamento en 345), en una fila
`flex items-center gap-1.5 flex-wrap` bajo el nombre. Se iguala a esa receta.

Ahora: `inline-flex items-center max-w-full bg-emerald-100 text-emerald-800
border border-emerald-300 rounded-full px-3 py-1.5 text-sm font-semibold
break-all`, solo texto (se quitó el ícono), en un contenedor `flex
items-center gap-1.5 flex-wrap mt-1.5 sm:hidden`. Se mantuvo `break-all` (y
no `whitespace-nowrap` como las otras) para que un usuario largo se parta en
vez de ensanchar la columna. Test:
`test_mobile_la_pildora_de_whatsapp_usa_la_receta_de_las_otras_vistas`.
