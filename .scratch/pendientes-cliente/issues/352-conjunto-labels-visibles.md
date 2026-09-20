# 352 — `/administracion/conjunto`: campos sin etiqueta visible

**Pedido original (Jesús):** "en esta vista /administracion/conjunto, los
formularios que contienen los inputs no se pueden identificar, si existe la
información, pero no sé cómo se llama cada uno de los campos, por ejemplo
para los horarios tengo esto 'EL CLUB / 9:30 AM - 7:30 PM / 9:30 AM - 2:00
PM / 2:00 PM - 6:00 PM / 573334004007' y no tengo la más mínima idea de lo
que dicen con relación a los horarios."

**Status:** implementado

## Causa raíz

`components/_inputs.html::input_texto()` (compartido, ~25 usos en toda la
app) nunca renderiza un `<label>` real -- el texto de `label` solo se usa
como `placeholder` (más `aria-label`, invisible a la vista). Eso funciona
en un formulario de ALTA (arranca vacío, el placeholder se ve), pero
`/administracion/conjunto` es un formulario de EDICIÓN -- todos sus campos
arrancan con un valor real, así que el placeholder nunca llega a mostrarse
y no queda ninguna pista visible de qué es cada campo.

## Fix

Nuevo parámetro `mostrar_label=False` (default) en `input_texto()` -- con
`True`, renderiza un `<label>` real arriba del input, sin tocar el resto
del comportamiento. Default en `False` a propósito: no reordena
visualmente ninguno de los ~25 usos existentes de este macro en el resto
de la app (la mayoría formularios de alta que sí arrancan vacíos, donde el
placeholder-como-label ya funciona bien). Activado explícitamente en las
10 filas de `/administracion/conjunto` (única pantalla reportada con este
problema hasta ahora).
