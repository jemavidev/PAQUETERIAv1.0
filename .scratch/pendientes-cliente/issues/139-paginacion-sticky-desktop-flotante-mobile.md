# 139 — Paginación: sticky arriba (desktop) + píldora flotante abajo (mobile), `/paquetes` y `/residentes`

**Pedido original (cliente):** trabajar la paginación (`Anterior 1 2 3 4 Siguiente`), pidiendo
alternativas de vista, luego iterado en varias rondas hasta el diseño final.

**Status:** implementado

## Implementación

- Skill `prototype`: 3 alternativas comparadas en vivo en `/residentes?variant=A|B|C` (numerada
  con elipsis, salto directo por número, cursor simple), más una 4ta "D" (cursor simple +
  sticky). Ganadora: **D**.
- Componente único `components/_paginacion.html`, una sola llamada por vista:
  - **Desktop (≥768px)**: `hidden md:flex`, `position: sticky; top: 16` (64px, altura real del
    header) — pegada justo debajo del header al scrollear. Sin lista de números, solo
    Anterior/Siguiente + "Página X de Y".
  - **Mobile (<768px)**: `md:hidden`, píldora `position: fixed`, ancho casi completo
    (`inset-x-3`), `bottom-16` (64px, flush arriba del footer de navegación fijo de la app),
    transparencia (`bg-white/80` + `backdrop-blur-md`) y bordes 100% redondeados. Oculta hasta
    que el usuario scrollea más allá de la barra de búsqueda/filtros (`IntersectionObserver`
    sobre un sentinel invisible).
  - Antes hubo una segunda paginación al final de la lista (arriba + abajo) — retirada por
    completo a pedido explícito, queda solo la de arriba.

## Bugs reales encontrados y corregidos en el camino

1. **Sticky inerte** (nunca se pegaba): el `<nav>` vivía envuelto en un `<div class="mt-4">`
   que no contenía nada más — su contenedor medía exactamente lo mismo que él, sin rango de
   scroll para "engancharse". Fix: se sacó del div envolvente.
2. **Footer de navegación fijo tapaba la píldora**: `.site-footer-mobile` (`position:fixed;
   bottom:0`, también visible para staff) quedaba en el mismo punto que la píldora
   (`bottom-0` original). Fix: `bottom-16`, flush arriba del footer.
3. **`margin-top` en elemento sticky no desaparece al pegarse**: `mt-2` + `top-16` dejaba la
   barra pegada a 72px en vez de 64px — hueco visible con el contenido asomando (se veía como
   una sombra). Fix: sin margen propio en el `<nav>`.
4. **Píldora se rompía tras cualquier búsqueda en vivo en `/paquetes`**: `_busqueda_filtros.html`
   reemplaza los resultados con `innerHTML`, y un `<script>` inyectado así nunca se ejecuta — el
   observer quedaba viendo un sentinel destruido. Fix: función global idempotente
   (`window.paqueteXInicPaginacionFlotante`) que `_busqueda_filtros.html` vuelve a llamar
   después de cada actualización.
5. **Segunda vuelta del mismo bug**: si `/paquetes` cargaba con un filtro angosto (≤1 página),
   la función ni se definía. Fix: la función se movió a `base.html` (siempre se ejecuta, nunca
   vía `innerHTML`).
6. **Orden de ejecución de scripts**: el `<script>` que LLAMA a la función vive temprano en el
   documento; la función se define al final de `<body>` (`base.html`). La llamada disparaba
   antes de que la función existiera -- la píldora quedaba muerta en la carga inicial (encontrado
   con Playwright real, no solo lectura de código). Fix: la llamada espera a `DOMContentLoaded`.
- Último registro de la lista tapado por la píldora en mobile: `pb-16` (64px, reducido de 128px
  inicial a pedido explícito) en el contenedor raíz de cada vista.

## Verificación

- Verificado con Playwright (navegador real, no solo lectura de código) en los 5 escenarios:
  carga inicial, scroll abajo, scroll arriba, después de buscar, scroll tras buscar — en
  `/paquetes` y `/residentes` por separado.
- Suite completa: 1023 passed (corrida durante la sesión).
- Pendiente: deploy a test.papyrus.com.co.
