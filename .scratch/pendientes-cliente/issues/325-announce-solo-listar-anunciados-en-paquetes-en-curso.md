# 325 — `/announce`: "Ya tiene paquetes en curso" solo lista ANUNCIADO

**Pedido original (cliente):** "Necesito que remuevas en la sección 'Ya tiene paquetes en curso:'
todos los paquetes que no tengan estado 'Anunciado', ya que esta vista es para anunciar o recibir
paquetes, no está diseñada para entregar o cancelar paquetes."

**Status:** implementado, pendiente desplegar a test.papyrus.com.co y que el cliente lo confirme.

## Alcance

Segundo ajuste de la serie sobre `/announce` (ver [[324]]). La sección "Ya tiene paquetes en
curso:" de la tarjeta Anunciar/Recibir (`components/_persona_resuelta.html`, issue 164) hoy lista
paquetes `ANUNCIADO` (link a Recibir) Y `RECIBIDO` (link a Entregar) de la persona identificada.
Se acota a listar SOLO `ANUNCIADO` -- `/announce` es una vista de anunciar/recibir, no de
entregar/cancelar (eso vive en `/paquetes`).

`paquetes_abiertos_de_persona` (`paquete_service.py`) NO se toca -- la usa también
`paquete_sincronizacion_service.py` para sincronizar snapshots, ahí sí necesita ANUNCIADO+RECIBIDO
por igual. El filtro a solo ANUNCIADO se aplica en los 2 call-sites de `announce_new.py` que
alimentan la tarjeta (camino Teléfono/WhatsApp directo y camino Ocupante).

Con eso, la rama RECIBIDO/"Entregar" del macro `tarjeta_persona_resuelta` queda inalcanzable --
se quita junto con el diccionario `estado_colores` (ya no hace falta distinguir color por estado
si solo hay uno).

## Implementación

- `app/web/routes/announce_new.py`: en `announce_identificar` y `announce_identificar_ocupante`,
  el resultado de `paquetes_abiertos_de_persona(...)` se filtra a
  `estado == EstadoPaquete.ANUNCIADO` antes de pasarlo a la plantilla.
- `app/web/templates/components/_persona_resuelta.html`: simplificado el bloque "Ya tiene paquetes
  en curso" a un solo camino (siempre enlaza a Recibir); quitado `estado_colores` y la rama
  Entregar; actualizado el comentario de cabecera.
- `tests/web/test_announce_new.py`: `test_identificar_telefono_con_recibido_muestra_link_entregar`
  reemplazado por `test_identificar_telefono_con_recibido_no_lo_lista` (persona con un paquete
  RECIBIDO ya no muestra la sección).

## Verificación

- `tests/web/test_announce_new.py` en verde.
