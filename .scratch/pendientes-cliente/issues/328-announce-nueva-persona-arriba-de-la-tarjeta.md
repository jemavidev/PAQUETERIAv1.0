# 328 — `/announce`: "+ Nueva persona" reubicado ARRIBA de la tarjeta Anunciar/Recibir

**Pedido original (cliente):** "coloca lo relacionado a '+ Nueva persona' arriba de los botones de
'Anunciar y Recibir'."

**Status:** implementado, pendiente desplegar a test.papyrus.com.co y que el cliente lo confirme.

## Alcance

Seguimiento a [[327]] (que ya deduplicaba los dos pares de botones vía JS, `data-nueva-persona`).
El cliente pidió además invertir el ORDEN visual: antes la lista de residentes → tarjeta
Anunciar/Recibir (preseleccionada o elegida) → "+ Nueva persona"; ahora lista de residentes → "+
Nueva persona" → tarjeta.

## Implementación

- `app/web/templates/announce_new/_identificar_unidad.html`: el bloque `<details data-nueva-
  persona>` se movió antes del cálculo de preselección + `#announce-unidad-accion`. El toggle JS
  de [[327]] (`form.html`, delegado sobre `#announce-resultado`) no depende del orden en el DOM
  (usa `getElementById`), así que sigue funcionando igual sin cambios.

## Verificación

- `tests/web/test_announce_new.py`: 81/81 en verde antes de sumar las mejoras de [[329]]/[[330]] en
  la misma sesión (91/91 al final).
