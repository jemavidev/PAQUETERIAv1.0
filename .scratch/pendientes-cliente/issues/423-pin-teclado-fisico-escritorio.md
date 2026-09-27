# 423 — PIN: teclear los números en escritorio sin usar el mouse

**Pedido original (Jesús, 2026-09-27):** "Seria bueno que solo se digite en la version de desktop los numeros y estos se
reflejen en el input, de esta forma al cargar esta vista simplemente se puedan digitar los numeros y se pueda acceder, esto
ya que en este momento es necesario presionar los botones de cada digito con el mouse. Este comportamiento es diferente a un
dispositivo mobil ya que en el dispositivo movil si seria facil presionar cada numero."

**Status:** verificado (`860699b`, confirmado por Jesús en test 2026-09-27)

## Alcance

- En la pantalla `/bloqueo` y en la capa de bloqueo, las teclas 0–9 (fila superior y teclado numérico) llenan el PIN,
  Retroceso borra y Enter envía, **sin depender del foco**: al cargar la vista se teclea y listo. Con 4 dígitos entra solo,
  como ya pasa.
- En móvil no cambia nada: teclado en pantalla y sin abrir el teclado del sistema.
- Relacionado: `.scratch/pin-operador-dispositivo` (tickets 03/04, `components/_teclado_pin.html`).

## Nota

Jesús observó (2026-09-27) que teclear ya funcionaba al cargar `/bloqueo`: en escritorio el campo del PIN toma el foco
(`data-enfocar`). Lo agregado cubre el caso en que el foco se pierde (un clic en cualquier parte de la pantalla o de la
capa): las teclas 0–9, Retroceso y Enter siguen llenando el PIN sin volver a los botones.
