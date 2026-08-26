# 182 — Unificar fuentes en TODA la app (no solo /paquetes)

**Pedido original:** "ahora lo que necesito es que unifiques todas las fuentes entre las vistas
del app."

**Status:** implementado

## Diagnóstico

Auditadas TODAS las plantillas del proyecto (`grep -rl "font-family\|fonts.googleapis\|@font-face"
templates/`), no solo las 2 vistas de la conversación. Resultado: 3 archivos con alguna
declaración de fuente --

1. `packages/list.html` -- ya sin regla activa (issue 180 la quitó, solo quedaba el comentario).
2. `base.html` -- `.site-header { font-family: system-ui, -apple-system, sans-serif; }`. Intencional
   y ya consistente con el default de Tailwind (`ui-sans-serif, system-ui, -apple-system, ...`) --
   no es un override "distinto", es básicamente el mismo stack. No se tocó.
3. **`announce_new/form.html`** -- tenía el MISMO problema que tenía `/paquetes` antes de [[180]]:
   Nunito Sans vía Google Fonts, `#vista-announce` como wrapper. Origen: issue 131 (ampliación B,
   2026-08-18) copió literalmente el tratamiento de `/paquetes` "porque es la misma audiencia" --
   nadie lo revirtió cuando se quitó de `/paquetes`.

Ningún otro archivo del proyecto define una fuente propia -- con esto, TODAS las vistas (incluida
`/announce`) quedan en el mismo stack por defecto de Tailwind/`base.html`.

## Cambio

- `announce_new/form.html`: eliminado el `{% block head %}` (preconnect + link de Nunito Sans +
  `<style>`) y el wrapper `<div id="vista-announce">` -- mismo patrón exacto que [[180]] aplicó a
  `packages/list.html`.

## Verificación

- Suite completa de `tests/web/`: **637/637**.
- Verificado en local (`localhost:8010`): `/announce` ya no carga fuentes de Google.
- Auditoría de cobertura: `grep` confirma que no queda ninguna otra plantilla con `font-family`/
  `fonts.googleapis`/`@font-face` propio en todo el proyecto.
- Pendiente: verificar en test.papyrus.com.co tras deploy.
