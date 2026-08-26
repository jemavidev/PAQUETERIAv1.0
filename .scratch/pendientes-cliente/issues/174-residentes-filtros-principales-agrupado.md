# 174 — `/residentes`: botones de filtro (Listar principales, Agrupar por apartamento, Limpiar)

**Actualización 1 (mismo día):** pedido de seguimiento -- "Mejora los botones de filtro para que
se asemejen a los botones o iconos en la vista de /paquetes" → los 3 botones pasaron de texto
plano a íconos cuadrados de 36px (mismo mecanismo EXACTO que `filtro_estado()` de `/paquetes`:
`icono_estado_base`, 3 estados suave/activo/opacado, repintado vía `data-*` + `ICONO_BASE`).
Nuevo ícono `estrella` en `icons.py` (Principal, azul) -- geometría calculada a mano (sin
referencia de producción, mismo criterio que `casa`/`email`/`candado`), pendiente verificar
visualmente en un browser real. `agrupado` reusa el ícono `casa` ya existente. Ver
`filtro_vista_residentes` en `components/_busqueda_filtros.html`.

**Actualización 2 (mismo día):** pedido de seguimiento -- "mejora el color de los iconos" →
"Agrupar por apartamento" pasó de índigo a violeta (índigo/`#6366F1` quedaba casi indistinguible
del azul/`#3B82F6` de "Listar principales", colores vecinos en la paleta -- a diferencia de los 4
colores de Estado en `/paquetes`, de familias totalmente distintas). Las tarjetas agrupadas
(`customers_manage/_resultados.html`) cambiaron a juego. **Bug real evitado:** `violet-*` nunca
se había usado en el repo -- a diferencia de `indigo-*` (ya compilado por
`packages/_resultados.html`), esas clases NO estaban en `tailwind.css`; sin reconstruirlo
(`npm run build:css`) las tarjetas hubieran quedado sin estilo en producción (el Dockerfile del
deploy nunca corre ese build, ver memoria `paquetex-tailwind-build`). `tailwind.css` reconstruido
y confirmadas las 8 clases nuevas presentes.

**Actualización 3 (mismo día):** "los colores siguen siendo muy palidos, hay uno azul y otro que
no se ve nada de lo palido que esta" → **bug real encontrado**: `base.html` referencia
`/static/css/tailwind.css?v=61` como cache-bust manual -- reconstruí el archivo en la
Actualización 2 pero nunca subí ese número, así que el navegador pudo seguir sirviendo el CSS
VIEJO desde caché (donde `violet-*` no tenía ninguna regla, renderizando sin color de fondo --
"no se ve nada" encaja exacto con ese síntoma). Subido a `?v=63` (dos bumps: uno por el rebuild de
la Actualización 2 que no se subió, otro por este). Adicional: `suave` (estado de reposo, sin
selección) subió de 500 a 600 -- un paso más oscuro/saturado, para que el color se note de
entrada sin depender de `activo`. Verificado con curl que `/static/css/tailwind.css?v=63` (la URL
que ahora referencia la página) responde 200 y trae `bg-blue-700`/`hover:bg-violet-700`.

**Actualización 4 (mismo día):** "que opciones de colores de botones me tienes para los 2 botones
'Listar principales y Agrupar por apartamento'?" → presentadas 4 combinaciones en vivo (Azul +
Violeta [la que había], Azul + Esmeralda, Azul + Teal, Ámbar + Azul invertido) — elegida "Ámbar +
Azul (invertido)": Principales pasa de azul a ámbar (`bg-amber-600/700/800`, `ring-amber-200`),
Agrupado pasa de violeta a azul (`bg-blue-600/700/800`, `ring-blue-200`) — rompe a propósito el
vínculo visual que antes tenía "Principales" con el badge azul "Principal" de la tabla, el cliente
lo eligió así explícitamente. Tarjetas de "Agrupar por apartamento" (`customers_manage/
_resultados.html`) actualizadas a juego (violeta → azul), mismo criterio de siempre. `tailwind.css`
reconstruido (`bg-amber-800`/`hover:bg-amber-700` eran clases nuevas, `blue-*` ya estaba
compilado) y `?v=63` → `?v=64`. Verificado en local: ícono ámbar para Principales, azul para
Agrupado + sus tarjetas.

**Pedido original:** "necesito unos botones de filtrado para los siguientes criterios (Listar
principales, Agrupar o listas por apartamento (donde se agrupen los residentes de un mismo
apartamento, incluso si ya se realizo una busqueda, con el fin de saber todos los integrantes de
un mismo apartamento), Limpiar filtros). Adicional para los botones de accion necesito que se
muestren siempre todos los botones posible, se veria mas unificado, solo deja activos los que
correspondan, los que no los dejas inactivos y grises como lo has echo antes." → aclarado con
pregunta de opción múltiple sobre CÓMO se ve "Agrupar por apartamento": el cliente eligió
"Tarjetas por apartamento" (reusa el patrón visual "Residentes de la unidad" que ya existe en el
modal Ver de `/paquetes`) en vez de una tabla con encabezados de grupo.

**Status:** implementado

## Decisiones inferidas (sin pregunta aparte, por precedente directo en el propio pedido/código)

- Los 3 botones viven DENTRO del mismo `<form>` de la barra de búsqueda (participan del fetch en
  vivo de [[173]], mismo mecanismo, sin JS nuevo que reinventar).
- "Listar principales" y "Agrupar por apartamento" son single-select con toggle-al-reclick --
  mismo criterio que ya usa `filtro_estado()` en `/paquetes` (clic en el ya activo vuelve a
  "todos"). Combinarlos no tiene sentido (agrupado ya muestra principal + secundarios por unidad),
  así que son mutuamente excluyentes.
- "Siempre todos visibles, grises los que no corresponden" (pedido explícito, "como lo has hecho
  antes"): mismo lenguaje visual que ya existe en el repo -- `boton`/`boton_apagado` de
  `_paginacion.html` (Anterior/Siguiente) y el ícono de Llamar sin teléfono en la propia tabla de
  `/residentes`. "Limpiar filtros" queda además con `disabled` real (no solo gris) cuando no hay
  nada que limpiar (`q` vacío Y `vista` vacía) -- clic no sería un no-op visible, es un no-op real.
- Botones con TEXTO, sin ícono nuevo -- ningún ícono existente en `icons.py` calza bien con
  "principal"/"agrupar por apartamento" y el proyecto documenta que los íconos hechos a mano se
  diseñan con cuidado ("verificados visualmente"); mejor texto plano que un ícono improvisado.

## Cambio

- `customers_manage.py`: `vista` (query param nuevo, `"principales"|"agrupado"|None`).
  - `_listar_principales`/`_buscar_principales`: mismo patrón que
    `_listar_todos_los_residentes`/`_buscar_residentes`, filtrando a Residente Principal activo
    (join contra `Ocupante`, no un filtro Python post-paginación).
  - `_agrupar_por_apartamento(db, personas_en_alcance, pagina)`: a partir del alcance (búsqueda
    activa, o TODOS los activos si no hay `q`), arma un grupo por cada Apartamento referenciado --
    con TODOS sus residentes activos (`_ocupantes_de`, ya existente), no solo los que matchearon
    -- así "Agrupar por apartamento" tras una búsqueda responde "quién más vive acá". Personas sin
    apartamento asignado no arman grupo, se listan aparte (`sin_apartamento`, solo en página 1).
    Paginado por APARTAMENTO (mismo `_POR_PAGINA=20`), no por persona.
- `customers_manage/_resultados.html`: nueva rama `{% if vista == 'agrupado' %}` -- tarjetas
  (fondo indigo, mismo estilo que "Residentes de la unidad" de `packages/_resultados.html`) en
  vez de la tabla plana; cada tarjeta = Torre/Apto + lista de sus residentes (nombre enlazado a la
  ficha, badge Principal, WhatsApp/llamada). La rama de tabla plana existente gana un filtro
  adicional cuando `vista == 'principales'` (mismo `resultados`, ya viene filtrado del backend).
  `paginacion(...)` ahora preserva `vista`+`q` en sus links (antes no hacía falta, `q` nunca
  convivía con paginación).
- `components/_busqueda_filtros.html`: `busqueda_filtros()` ahora acepta un `{% call %}` opcional
  (`caller()`) para inyectar contenido extra en la misma fila del form -- así `search.html` no
  necesita un `<form>`/fetch propios para estos 3 botones, reusa el mecanismo entero de [[173]].
  El `<script>` del macro gana soporte genérico para un campo oculto adicional
  (`[data-vista-hidden]`, análogo a `[data-estado-hidden]` pero sin acoplarse a Estado de
  paquete) -- ausente en `/paquetes` (no lo usa), presente en `/residentes`.
- `customers_manage/search.html`: los 3 botones (`data-vista-boton="principales"`,
  `data-vista-boton="agrupado"`, `data-vista-reset`), dentro del `{% call %}`.

## Verificación

- 13 tests nuevos en `test_customers_manage.py`: botones siempre visibles, `aria-pressed` refleja
  la vista activa, "Limpiar filtros" deshabilitado/habilitado según corresponda, filtro
  Principales (con y sin búsqueda -- requiere `confirmar_ocupante`, `agregar_ocupante` ya no
  promueve a principal solo), Agrupar por apartamento (agrupa correctamente, incluye a TODOS los
  del apartamento aunque la búsqueda solo matcheó a uno, incluye "sin apartamento" aparte,
  paginado por apartamento real del catálogo cerrado), y que el fragmento en vivo respeta `vista`.
- Suite completa: 300/300 (`test_customers_manage.py` + `test_packages.py`).
- Verificado en local (`localhost:8010`) con curl: cada `vista` (íconos + tarjetas), combinada
  con `q`, paginación preservando `vista`, estado activo/opacado de los íconos al togglear.
- Pendiente: verificar en test.papyrus.com.co tras deploy (especialmente el ícono `estrella`
  calculado a mano -- confirmar que se ve bien en un browser real).
