# 24 — `/ayuda`: contenido actualizado + ícono correcto de producción

**Pedido original (cliente, item 8 del recorrido pantalla por pantalla):**
"Necesito que tenga el contenido de https://paquetex.papyrus.com.co/help,
pero actualizado a las nuevas cosas que se manejan en paquetes. El look and
feel debería ser similar. Más adelante estaremos actualizando el contenido
de esta sección basado en lo que en realidad maneje el app paquetex.
Necesito que se use el ícono
'M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278
2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0
9 9 0 0118 0z' utilizado en la vista de producción." (mismo pedido mobile y
desktop).

**Vista:** `ayuda/form.html` + ícono `iconos_nav.ayuda` (footer, mobile y
desktop).

**Status:** verificado

## Qué hacer

1. Traer el contenido de producción (`/help`), actualizado a lo que el
   rebuild REALMENTE maneja.
2. Reemplazar el ícono actual de "Ayuda" (solid, circle-question) por el
   path outline dado, que es el que usa producción de verdad.

## Qué se hizo

- **Ícono**: `ICONOS_NAV["ayuda"]` en `icons.py` reemplazado por el path
  exacto dado (outline, Heroicons). Se agregó `contorno=true` a las 2
  llamadas de `enlace_nav_footer('/ayuda', ...)` en `base.html` (mobile +
  desktop) -- el macro necesita ese flag para renderizar el wrapper SVG
  correcto (`viewBox 24x24 stroke`, no `20x20 fill`). El comentario de
  `icons.py` que afirmaba que el ícono de Ayuda YA era el de producción
  era incorrecto -- corregido.
- **Contenido**: extraído de `paquetex.papyrus.com.co/help` vía fetch
  directo (no inventado). Se verificó primero contra el dominio del
  rebuild (`grep` en `src/app/domain/` de "tarifa/precio/pago/payment/fee"
  -- CERO resultados) que el rebuild **no modela tarifas, horarios ni
  pagos** -- por eso esas 3 secciones de producción (Tarifas del
  Servicio, Horarios de Atención, Métodos de Pago) se OMITIERON a
  propósito, en vez de presentarlas como si fueran una función real del
  software cuando no lo son. Lo que sí se trajo y adaptó a la
  funcionalidad real del rebuild: qué es PAQUETEX, cómo funciona (4
  pasos: anuncio/recepción/consulta/entrega), código de seguimiento de 4
  caracteres + `/consultar`, notificaciones por 4 canales, autogestión de
  datos vía `/entrar` con OTP de 2 dígitos (tickets 13-14 de esta misma
  ronda), seguridad (fotos de evidencia). Las 6 preguntas específicas del
  rebuild que ya existían (guía opcional, anunciar sin teléfono propio,
  etc.) se conservaron tal cual.
- Recompilado `tailwind.css` (`list-decimal`, `list-inside`, `font-mono`
  nuevos) + bump de cache-busting a `v=17`. Verificado con un render
  aislado (`TestClient` + `file://`) antes de tocar el sitio en vivo.

## Verificación

- [x] Captura confirma el ícono outline correcto en el footer y el
      contenido nuevo en `/ayuda` (mobile y desktop).
- [x] Suite de tests sin regresiones (24 passed en test_ayuda.py +
      test_layout.py).
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo.

## Pendiente de confirmar con el cliente

Se omitieron Tarifas/Horarios/Métodos de pago de producción porque el
rebuild no los modela como funcionalidad real todavía -- si el cliente
prefiere tenerlos igual (como texto informativo, aclarando que es
información de contacto/negocio y no algo que la app "maneja"), se agregan
en una ronda siguiente.
