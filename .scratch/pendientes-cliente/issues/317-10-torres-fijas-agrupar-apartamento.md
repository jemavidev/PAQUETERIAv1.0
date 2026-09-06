# 317 — "Agrupar por apartamento" con número exacto: 10 Torres SIEMPRE visibles

**Pedido original (cliente):** en `/residentes`, después de buscar un número de apartamento
específico (ej. "apt302") y presionar "Agrupar por apartamento", como el edificio SIEMPRE tiene
exactamente 10 Torres, mostrar las 10 SIEMPRE (tengan o no residentes), en desktop, en este
layout: FILA 1 (T01 T02 T03), FILA 2 (T04 T05 T06), FILA 3 (T07 T08 T09), FILA 4 (vacío, T10,
vacío -- T10 centrada). Pidió sugerencias de LOOK: cards, acordeón, secciones, u otra idea --
y cómo tratar a los residentes sin apartamento asignado (que YA tienen su propio tratamiento
hoy, separado del agrupado).

**Status:** implementado, desplegado a test.papyrus.com.co (2026-09-05, commit `bcac30d`) --
pendiente que el cliente lo confirme visualmente (extensión de Chrome no disponible en esta
sesión). Cliente eligió **Variante A** ("me parece perfecta en todas las
vistas") sobre acordeón/secciones. Prototipo (código + ruta throwaway) BORRADO tras plegar la
variante ganadora al código real, según el proceso de la skill `prototype` -- este archivo queda
como el registro de las 3 variantes y la decisión (no se armó una rama git aparte para el
throwaway: se siguió la convención propia de este proyecto de dejar todo en
`.scratch/pendientes-cliente/`, no se hicieron operaciones de git no pedidas).

Verificado end-to-end contra datos reales (`localhost:8010`, apartamento 302 real: Torre 1 con 4
ocupantes, Torre 5 con 1, Torre 10 con 2, las otras 7 vacías) -- el HTML devuelto coincide
exactamente con la BD. 4 tests nuevos, suite completa en verde
(`test_packages.py`/`test_layout.py`/`test_customers_manage.py`/`test_search.py`).

## Implementación real

`_agrupar_10_torres_fijas(db, numero_apartamento)` (nueva, en `customers_manage.py`) -- arma las
10 combinaciones Torre 1..10 × número buscado, resuelve cuáles existen en el catálogo y sus
ocupantes activos (`_ocupantes_de`, ya existente). La ruta `/residentes` detecta cuándo aplica
(`_ESQUEMA_APARTAMENTO_RE.match(termino)`, el mismo regex `apt<número>` que ya usaba
`_buscar_residentes` para esta búsqueda) y en ese caso reemplaza `_agrupar_por_apartamento` por la
función nueva -- el resto de "Agrupar por apartamento" (sin búsqueda, o búsqueda por nombre/
teléfono) sigue exactamente igual que antes.

`sin_apartamento` queda vacío a propósito en este modo -- el propio match de `apt<número>` en
`_buscar_residentes` ya exige que la Persona TENGA apartamento, así que ese caso no puede ocurrir
por este camino (confirmado con un test dedicado). El bloque "Sin apartamento asignado" NO se
tocó para el resto de la vista.

Grid fijo `lg:grid grid-cols-3` (SOLO desktop, pedido explícito) con Torre 10 centrada vía un
`<div>` spacer antes de su celda -- mobile (`lg:hidden`) cae a una lista vertical apilada de las
mismas 10 tarjetas, sin grid.

## Prototipo (`/home/stk/.claude/skills/prototype`, throwaway -- BORRAR antes de mergear)

Probar en vivo: `/residentes?prototype=torres10&variant=A` (o `B`/`C`), sesión de staff activa.
Datos 100% falsos (`_prototipo_10_torres_mock`/`_prototipo_sin_apartamento_mock` en
`customers_manage.py`) -- simulan buscar "apt302": Torres 1/3/5/8 con residentes (variando
cantidad, con/sin Principal, con/sin teléfono para ver los íconos apagados), 6 vacías.

- **Variante A -- Grid fijo 3+3+3+1**: 10 tarjetas en grid de 3 columnas (mismo estilo azul/
  card ya usado hoy para "Agrupar por apartamento"), Torre 10 centrada vía un spacer antes de su
  celda. Vacías en gris con "Sin residentes". Más fiel al layout EXACTO que pidió el cliente.
- **Variante B -- Acordeón**: una fila compacta por Torre (punto azul/gris + conteo), se expande
  al hacer clic. Más compacto en alto, pero exige clics para ver contenido -- distinto al layout
  de grid pedido.
- **Variante C -- Secciones**: separa "Con residentes" (arriba, tarjetas completas) de "Sin
  residentes" (abajo, chips compactos con solo el número de Torre) -- separa la señal (quién
  vive ahí) del ruido de las Torres vacías, pero NO respeta el orden/posición fija de Torre 1-10
  que pidió el cliente.

Los 3 mantienen: paleta azul ya fijada para esta función, badge "Principal", íconos WhatsApp/
Llamar, y el bloque "Sin apartamento asignado" tal cual ya existe hoy (tarjeta gris aparte, sin
agrupar) -- eso no se tocó, solo se muestra en contexto para confirmar que sigue sirviendo.

## Pendiente

Que el cliente elija variante (o pida mezclar partes) antes de implementar la lógica real de
backend (hoy `_agrupar_por_apartamento` solo trae Torres que YA tienen match -- hace falta una
función nueva que arme las 10 combinaciones Torre+número fijas cuando la búsqueda es un número de
apartamento exacto).
