# 52 — `/consultar`: foco condicional tras buscar + gestos táctiles en el visor de fotos

**Pedido original (cliente):** "En el dispositivo movil, despues de consultar un
codigo exitosamente o no, el focus se deberia perder para los campos del
formulario de esta vista especifica, esto con el fin queno se active el
teclado del dispositivo mobil. Adicional para el visualizador de las
imagenes, seria bueno que este tenga una interfaz que permita una
transision natural (UX) esto ya que en la actualidad no se si se peuda
hacer pitch to zoom o si se pueda deslizar entre imagenes con los dedos sin
tocar las flechas."

**Status:** implementado

## Contexto

Continuación del pase de vistas móvil ([[49]]) sobre `/consultar`, la
siguiente vista pública en el orden acordado con el cliente.

## Implementación

**1. Foco condicional específico de esta vista.** `/consultar` nunca usa
una variable `error` (a diferencia del resto del app, donde el criterio ya
existente es `autofocus=(not error)`, ver [[49]]) — tiene tres resultados
distintos (formulario limpio / `paquete` encontrado / `sin_resultados`), así
que necesitó su propia condición en vez de reutilizar el patrón genérico:

```jinja
autofocus=(not paquete and not sin_resultados|default(false))
```

Solo autofocus en la carga limpia del formulario; ya consultado (con o sin
resultado) no reactiva el teclado, dejando visible el resultado que aparece
debajo. Archivo: `app/web/templates/search/form.html`.

**2. Gestos táctiles reales en el visor de fotos**, reemplazando la versión
2026-08-02 (que se apoyaba en el zoom nativo del navegador y excluía swipe a
propósito por conflicto de eventos táctiles con ese zoom nativo). Diseño
nuevo: un solo intérprete de gestos en JS vanilla que decide en `touchstart`
(2 dedos = pinch; 1 dedo = pan si ya hay zoom, swipe si no) y mantiene esa
decisión hasta `touchend`, con `touch-action: none` dándole control
exclusivo sobre la imagen:

- Pinch zoom 1x-4x con pan limitado a los bordes de la imagen ampliada.
- Doble tap alterna 1x/2x (funciona tanto para hacer zoom como para
  deshacerlo — bug propio detectado y corregido antes de desplegar: la
  primera versión solo detectaba el doble tap partiendo de `swipe`, no de
  `pan`, así que doble tap para des-zoomear no hacía nada).
- Swipe de 1 dedo sin zoom activo, con la foto siguiendo el dedo en vivo y
  una transición de deslizamiento (salida + entrada animadas) al soltar por
  encima del umbral.
- Botones anterior/siguiente, flechas de teclado y Escape quedan intactos —
  los gestos son complemento, no reemplazo.

Archivo: `app/web/templates/components/_visor_fotos.html`.

## Verificación

- `tests/web/test_search.py`: 3 tests nuevos para el foco condicional (19
  en el archivo, todos pasan).
- Suite completa (`tests/data_model tests/web`) sin regresiones.
- Sintaxis del `<script>` verificada con `node --check` (no hay framework
  de testing JS en el proyecto) y el Jinja con `Environment.parse()`.
- Pendiente: confirmar en `test.papyrus.com.co`, en un dispositivo táctil
  real, que el foco no reactiva el teclado y que pinch-zoom/pan/swipe/doble
  tap se sienten naturales — es la única parte de este cambio que no se
  puede validar sin un touchscreen real.
