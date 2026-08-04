# 23 — Toast: texto de la notificación un poco más grande

**Pedido original (cliente):** "necesito que las notificaciones sean un
poco más grandes (class="text-sm text-slate-700 flex-1"), en este momento
se ubican en la parte inferior de la pantalla, pero están muy pequeñas".

**Componente:** `components/_toast.html` (compartido por TODA la app --
cualquier vista que use `{{ toast(...) }}`, no solo una pantalla puntual).

**Status:** verificado

## Qué hacer

`text-sm` (14px) → `text-base` (16px) en el `<p>` del mensaje del toast.

## Qué se hizo

`Edit` de una sola línea. Sin clases nuevas para Tailwind (`text-base` ya
estaba compilado); sin tests que dependan del texto/clase literal.

## Verificación

- [x] Captura confirma el texto más grande en un toast real (16px,
      medido con Playwright `getComputedStyle`, antes 14px).
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo.
