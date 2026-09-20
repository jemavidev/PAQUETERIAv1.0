# 367 — `/announce`: ícono de "Nuevo residente" más grande, redondo y con fondo

**Pedido original (cliente):**
"Necesito que para la vista /announce cambies el icono (<path
stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
d="M18 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 11-6.75
0 3.375 3.375 0 016.75 0ZM3 19.235v-.11a6.375 6.375 0 0112.75
0v.109A12.318 12.318 0 019.374 21c-2.331 0-4.512-.645-6.374-1.766Z">)
por uno mas grande, similar a los que venimos utilizando en el aplicativo,
este debe ser relacionado con 'Agregar usuario', recuerda debe ser el mismo
esquema que para los iconos de la columna Accion de las diferentes vistas
'redondo, con fondo'."

**Status:** implementado

## Alcance

- El ícono del desplegable "Nueva persona" (ahora "Nuevo residente", issue
  368) de `/announce`: hoy es el "user-plus" outline de `agregar_persona`
  a 16 px, sin fondo.
- Pasa a ser un botón circular con fondo tintado, el mismo esquema
  (`chip_icono`, `components/_badge.html`) que los íconos de la columna
  Acción de `/paquetes` y `/residentes`, con un glifo sólido de "agregar
  usuario" (la mayoría de los íconos de la app son sólidos, ver
  `icons.py`) y más grande.
- Aplica a los dos lugares de `/announce` donde vive ese desplegable: la
  lista de residentes de una unidad y la sugerencia de Contacto externo.

## Implementación

- `icons.py`: la clave `agregar_persona` pasa del path OUTLINE (Heroicons
  "user-plus", 24x24, `stroke`) al path SOLID (Heroicons "user-plus", 20x20,
  `fill="currentColor"`) -- mismo lenguaje visual que la mayoría de los
  íconos de la tabla.
- Nuevo componente `components/_resumen_nuevo_residente.html`: el `<summary>`
  del desplegable, compartido por `_identificar_unidad.html` y
  `_identificar_con_sugerencia.html` (antes cada uno tenía su propio
  `<summary>` duplicado). El ícono va en un botón circular de 36 px con
  `chip_icono('blue', tam='h-9 w-9')` -- el MISMO macro que arma los íconos
  de la columna Acción de `/paquetes` y `/residentes` -- con el glifo a 20 px
  adentro.
- El área táctil del resumen pasó de 24 px de alto a 36 px.

## Verificación

- `tests/web/test_announce_new.py` y
  `tests/web/test_announce_sugerencia_contacto_externo.py`: no fijan clases,
  pero sí que el texto sigue presente (ver issue 368).
- Ninguna clase nueva del componente: ya estaban en el `tailwind.css`
  compilado.
- `agregar_persona` no se usa en ninguna otra vista del repo (verificado):
  el cambio de glifo no afecta nada fuera de `/announce`.
- Navegador a 390 px: el chip mide 36x36, fondo azul claro
  (`rgb(219, 234, 254)`), sin scroll horizontal; con la tarjeta seleccionada
  o el desplegable abierto sigue siendo el único ícono de ese tamaño en la
  fila.
- Pendiente: confirmación visual del cliente y deploy a test.papyrus.com.co.
