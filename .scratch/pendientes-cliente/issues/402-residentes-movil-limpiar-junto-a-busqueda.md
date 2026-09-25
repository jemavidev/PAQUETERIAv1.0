# 402 — `/residentes` móvil: "Limpiar filtros" junto a la búsqueda, vistas en la 2da fila

**Pedido original (Jesús):** "para la vista /residentes, los íconos de filtro ... 'Limpiar filtros' deberá estar al
lado de la barra de búsqueda, los otros tres íconos deberían comportarse igual que como se ven en la vista de
/paquetes ... (Fila 1: Barra de búsqueda + Botón Limpiar filtros, Fila 2: Botones Listar principales + agrupado +
sin_apartamento)" ... "ten presente la vista de paquetes, esta tiene unos tamaños y espaciados específicos". Luego:
"aplícalo pero solo a la vista móvil".

**Status:** implementado (localhost), pendiente confirmar en vivo

## Decisiones (acordadas)

- Fila 1: búsqueda + "Limpiar filtros" en el lugar y tamaño del "+" de `/paquetes` (36 px), con su apagado de siempre.
- Fila 2: Principales / Agrupado / Sin apartamento repartidos a todo el ancho (`justify-between`), como los estados
  de `/paquetes`; mismos tamaños y espaciados.
- Solo móvil (< 768 px, mismo corte `md:` de la barra); escritorio queda igual (Limpiar al final).

## Verificación

- `test_customers_manage.py` + `test_residentes_movil_tarjetas.py`: 201 en verde (sin ajustes). Tailwind reconstruido, `?v=107`.
