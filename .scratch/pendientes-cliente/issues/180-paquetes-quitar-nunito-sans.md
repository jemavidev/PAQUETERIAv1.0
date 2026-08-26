# 180 — `/paquetes`: quitar Nunito Sans, unificar tipografía con el resto de la app

**Pedido original:** seguimiento a [[179]] -- "el problema no es la barra, el problema parece ser
el header, compara el header entre las vistas /consultar = /residentes, pero es diferente de
/paquetes" → diagnosticado: el `<header>` real (logo + nav) es byte-idéntico en las 3 vistas
(confirmado con `diff`, única diferencia `aria-current`, esperado) -- lo único objetivamente
distinto era que `/paquetes` carga Nunito Sans (Google Fonts) mientras `/residentes` y
`/consultar` usan la fuente por defecto del sitio, y el título justo debajo del header compartido
se siente "distinto" por eso → confirmado: "sí, quítalo."

**Status:** implementado

## Cambio

- `packages/list.html`: eliminado el `{% block head %}` completo (2 `<link rel="preconnect">` +
  el `<link>` de Nunito Sans + el `<style>#vista-paquetes{font-family:...}`) y el wrapper
  `<div id="vista-paquetes">` -- su único propósito era darle ese `font-family` a todo su
  contenido (grid + modal Recibir), sin la fuente custom ya no cumple ninguna función. `/paquetes`
  ahora hereda la misma fuente por defecto que el resto de la app (definida en `base.html`,
  `system-ui, -apple-system, sans-serif`).
- Nunito Sans había sido pedido explícito el 2026-08-17 (comparación de 7 candidatas) -- se revierte
  esa decisión a pedido igual de explícito, no es un descuido.

## Verificación

- Suite completa: 307/307 (`test_customers_manage.py` + `test_packages.py`).
- Verificado en local (`localhost:8010`): `/paquetes` ya no carga fuentes de Google ni el wrapper
  `#vista-paquetes` -- confirmado con curl (0 ocurrencias de "Nunito"/"fonts.googleapis"/
  "vista-paquetes" en el HTML servido).
- Pendiente: verificar en test.papyrus.com.co tras deploy.
