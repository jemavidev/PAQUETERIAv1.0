# 351 — `/anunciar`: unificar tipografía del aviso de privacidad con el texto del checkbox de T&C

**Pedido original (Jesús):** "para esta sección [texto del checkbox de T&C +
aviso de privacidad] conviertan esto al mismo formato y que se vea igual las
2 secciones, en este momento hay una que tiene diferente tipo de fuente o el
tamaño incorrecto. Corrígelo."

**Status:** implementado

## Contexto

`CODE/src/app/web/templates/announce/form.html` — el checkbox de Términos y
Condiciones y el aviso de privacidad agregado debajo (grilling 2026-09-18)
usaban clases de Tailwind distintas:

- Texto del checkbox: `text-sm text-slate-800`
- Aviso de privacidad: `text-xs text-slate-600`

El aviso de privacidad se veía notablemente más chico y más claro que el
texto del checkbox, aunque ambos viven en la misma tarjeta y deberían leerse
como una sola unidad.

## Fix

Unificado el aviso de privacidad a `text-sm text-slate-800`, igual que el
texto del checkbox.

## Ronda 2 (mismo día)

**Pedido (Jesús):** "la conviertas en una sola, veo que manejas 2 etiquetas
label y p" -- aunque ya se veían iguales, seguían siendo 2 elementos HTML
distintos (`<label for="acepta_tyc">` + `<p>`).

**Fix:** fusionados en un solo `<label for="acepta_tyc">`; el aviso de
privacidad pasa a un `<span class="block mt-1">` interno para conservar el
salto de línea visual. Los links de Términos y de Privacidad siguen
funcionando normal -- un click en un `<a>` anidado navega, no tilda además
el checkbox (el comportamiento por defecto de `<label>` solo se dispara si
el click cae fuera de cualquier elemento interactivo anidado).
