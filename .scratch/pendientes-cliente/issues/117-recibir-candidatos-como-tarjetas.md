# 117 — "¿A nombre de quién es?" en Recibir: tarjetas en vez de select

**Pedido original (cliente):**
"Remueve esto '¿A nombre de quién es? (opcional)', necesito ahorrar
espacio. Necesito que para esta lista 'Dejar como está' muestres todos
los residentes que existen solo para seleccionar, si puedes coloca 2 en
una misma fila, de lo contrario no, adicional si tienes ya una
preseleccion deja que se muestre, solo para saber cual esta
seleccionado."

**Status:** implementado

## Implementación

- `_recibir_paquete.html`: se quita la etiqueta "¿A nombre de quién es?
  (opcional)" y el `<select>` con "Dejar como está" -- reemplazado por
  tarjetas de selección de un clic (mismo lenguaje visual que "Corregir
  destinatario", issue 84), en grid de 2 columnas (`grid-cols-2`), con
  "Nuevo residente" a ancho completo (`col-span-2`) al final.
- El candidato que coincide con `recipient_name`/`recipient_phone`
  ACTUALES del paquete lleva un badge "Actual" -- puramente informativo,
  NO marca el radio como `checked`. Decisión deliberada: si el candidato
  actual quedara pre-marcado, enviar "Recibir" sin tocar nada mandaría
  igual `candidato_idx`, disparando `corregir_destinatario` de nuevo --
  eso apagaría la advertencia de nombre no coincide (issue 102) aunque no
  hubiera corrección real. Sin nada marcado por defecto, el comportamiento
  de "no tocar = no cambia nada" se mantiene exacto a como era con
  "Dejar como está" en el `<select>` viejo.
- `modal_recibir` gana los parámetros `recipient_name`/`recipient_phone`
  (los dos call sites -- `/paquetes` y `/announce` -- los pasan) para
  poder calcular el badge.
- `tailwind.css` recompilado (`?v=44`) -- clases nuevas (`text-[10px]`,
  `peer-checked:bg-blue-50`, `peer-checked:border-blue-600`) no estaban
  compiladas todavía.

## Verificación

- `tests/web/test_packages.py`: tests actualizados para las tarjetas en
  vez del `<select>` viejo, y nuevo test confirmando el badge "Actual"
  en el candidato correcto sin marcar ningún radio como `checked`.
- Playwright contra el servidor local real.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
