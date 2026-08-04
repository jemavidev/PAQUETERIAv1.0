# Design System PaqueteX — contrato de trabajo

Léeme primero antes de tocar cualquier componente nuevo.

## Reglas de interacción (fijas, no renegociables sin que el usuario lo pida)

1. Trabajo estrictamente componente por componente. Nunca generar todos los componentes de una vez.
2. Para el componente en turno, presentar 3 opciones de diseño distintas basadas en Tailwind, con
   descripción breve del enfoque de cada una (no el código completo todavía).
3. Después de presentar las 3 opciones, detente y espera. El usuario responde con el formato:
   `Opcion elegida: [numero] / Comentarios: [ajustes]`
4. Solo después de recibir esa elección se entrega el código final: un macro Jinja2 reutilizable en
   `src/app/web/templates/components/_<nombre>.html` (el REBUILD — `src/app/web/templates/`, no el
   legacy `src/templates/`), usando `{% macro %}...{% endmacro %}`, no `{% include %} con with`.
5. Mobile-first: un único bloque adaptativo con prefijos `sm:`/`md:`/`lg:` — prohibido crear
   plantillas separadas por dispositivo.
6. Alpine.js / HTMX solo se integran si la funcionalidad lo exige — no por defecto.
7. Memoria de diseño: todo componente nuevo hereda el vocabulario visual ya fijado (ver
   `tokens.md`) — no reinventar radios, sombras, anillos de foco ni colores.
8. Cada componente tiene su propio archivo de preview visual (Tailwind vía CDN, solo para ver en
   navegador local — no es el código de producción) en `previews/<nombre>.html`. Al elegir opción
   final, ese preview se actualiza para dejar SOLO la opción elegida.

## Dónde está todo

- **`IMPLEMENTACION.md`** — guía de cierre: qué se corrigió contra producción y checklist de
  migración página por página. Empezá ahí si vas a implementar el tema en el rebuild.
- `tokens.md` — fuente de verdad del vocabulario visual (colores por rol semántico, radio, sombra,
  anillo de foco). Léelo antes de proponer cualquier opción nueva.
- `previews/*.html` — un archivo por componente, abrir directo en el navegador (doble clic).
- `../../src/app/web/templates/components/_*.html` — macros Jinja2 finales, listos para usar en
  plantillas reales del rebuild.

## Estado actual (2026-07-29)

| # | Componente | Estado |
|---|---|---|
| 1 | Botones | ✅ Cerrado — Variante A (vívida): `_botones.html` |
| 2 | Badges de estado (ANUNCIADO/RECIBIDO/ENTREGADO/CANCELADO) | ✅ Cerrado — Opción 2 (fondo suave/pill): `_badge.html` |
| 3 | Inputs de texto + validación | ✅ Cerrado — Opción 1 (Clásico): `_inputs.html` |
| 4 | Tarjetas de paquete y cliente | ✅ Cerrado — Opción 1 (Compacta de lista): `_tarjetas.html` |
| 5 | Formularios de flujo (anunciar/recibir/entregar) | ✅ Cerrado — Opción 1 (Tarjeta única): `_formularios.html` |
| 6 | Tablas de datos | ✅ Cerrado — Opción 1 (Scroll horizontal) + acciones CRUD como íconos: `_tablas.html` |
| 7 | Timeline de seguimiento | ✅ Cerrado — Variante C (caja con badge + chips), solo el estado actual con color: `_timeline.html` |
| 8 | Alertas / notificaciones (toast) | ✅ Cerrado — Toast flotante con auto-dismiss (`bottom-20`, no tapa la nav inferior fija): `_toast.html` |
| 9 | Modales / confirmación | ✅ Cerrado — Centrado siempre + selects con <5 opciones como chips (sin JS): `_modales.html` |
| 10 | Zona de carga S3 (fotos) | ✅ Cerrado — Arrastrar y soltar (progresivo, límite real en servidor): `_carga_fotos.html` |
| 11 | Búsqueda y filtros | ✅ Cerrado — Barra unificada + chips de estado con la gama de color del proyecto: `_busqueda_filtros.html` |
| 12 | Paginación | ✅ Cerrado — Numerada con ventana ±2, `params` genérico (no filtros hardcodeados): `_paginacion.html` |
| 13 | Breadcrumbs / nav secundaria | ✅ Cerrado — Encabezado contextual con volver integrado: `_breadcrumbs.html` |
| 14 | Empty states | ✅ Cerrado — Ícono + texto + acción sugerida (distingue sin-resultados de vacío-real): `_estado_vacio.html` |
| 15 | Estados de carga / skeleton | ✅ Cerrado — Spinner centrado simple, reutiliza el spinner de Botones: `_estado_carga.html` |
| 16 | Confirmación de anuncio (página de éxito) | ✅ Cerrado (2026-07-30) — Opción 1 (Recibo con código destacado): `_confirmacion.html` |

## Design system completo ✅ — migración completa ✅

Los 16 componentes están cerrados. Cada uno tiene su macro final en
`../../src/app/web/templates/components/_*.html`, su preview aprobado en `previews/*.html`, y su
sección correspondiente en `tokens.md` (fuente de verdad del vocabulario visual).

**Migración terminada (2026-07-30):** todas las plantillas reales del rebuild usan ya estos
componentes — ver el checklist completo en `IMPLEMENTACION.md` sección 5. `announce/confirmacion.html`
era la última pendiente; motivó el componente 16 porque ninguno de los primeros 15 cubría una
"página de éxito".

## Siguiente paso

No queda trabajo de diseño ni de migración pendiente. El próximo trabajo natural sobre el tema,
cuando el usuario lo pida, son los ítems sueltos que quedaron anotados en `IMPLEMENTACION.md`
sección 7 (íconos de header de escritorio, `_iconos.html` centralizado, uso de `papyrus-logo.png`)
— ninguno es urgente, ninguno se empieza sin que el usuario lo pida explícitamente.

Nota de contexto del proyecto: los primeros componentes de este design system se generaron bajo un
sistema de orquestación de agentes ("AgentX") que pertenecía a un proyecto anterior, no a PaqueteX
— se retiró por completo del repo el 2026-08-04 (sin backup, nunca fue parte de este rebuild). De
aquí en adelante el trabajo es directo, sin sub-agentes ni protocolo de dispatch.
