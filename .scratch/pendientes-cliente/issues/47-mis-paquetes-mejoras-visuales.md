# 47 — `/mis-paquetes`: color de tabs (ya en vivo), ubicación más natural, identificar ocupante

**Pedido original (cliente):** "existe la posibilidad de mejorar la forma en como se ve la vista
/mis-paquetes con relacion a los paquetes (anunciados, recibidos, entregados y cancelados),
inicialmente que se aplique un color a los tabs de cada estado de los paquetes. Adicional que lo
relacionado a (Conjunto, torre y apartamento se vea mas natural en esta seccion, que alternativas
me das para esto). Por ultimo que posibilidad existe en que coloques alque que identifique a cada
usuario en esta vista, de forma que a simple vista se puedan diferenciar los paquetes que le
pertenecen a uno y a otro ocupante."

**Status:** en diseño — 3 puntos, distinto estado cada uno (ver abajo)

## Punto 1 — Color en los tabs: ya está en producción

Se implementó hoy mismo en el issue 43 (commit `75f79bc`, verificado en vivo) — cada tab colorea su
texto cuando está activo con el mapeo real de producción: Anunciados ámbar, Recibidos azul,
Entregados verde, Cancelados rojo. Es posible que el cliente no lo haya visto todavía en vivo, o
que lo que pide sea MÁS fuerte que solo el texto (ej. fondo de color, no solo texto) — pendiente de
confirmar cuál de las dos cosas.

## Punto 2 — Conjunto/Torre/Apartamento "más natural": alternativas

Hoy se muestra como una sola línea de texto gris plano, todo en MAYÚSCULAS (normalización de
`snapshot_conjunto`/`torre`/`apartamento`): `LAS FLORES · TORRE A · APTO 502`. Se construyen
alternativas visuales (ver preview) — no requiere cambios de datos, solo de presentación.

## Punto 3 — Identificar a qué ocupante pertenece cada paquete: bloqueado por alcance de datos

Hallazgo real antes de diseñar nada: `/mis-paquetes` (`customer_paquetes.py`) filtra
EXCLUSIVAMENTE por el teléfono de la sesión actual (`announced_by_phone == persona.telefono OR
recipient_phone == persona.telefono`) — **nunca muestra paquetes de otro Ocupante del mismo
Apartamento**. Hoy, cada sesión ve solo sus propios paquetes; no hay dos ocupantes que diferenciar
en la misma pantalla, porque la pantalla ya está recortada a uno solo.

Para que el pedido tenga sentido, primero hay que decidir si `/mis-paquetes` cambia de alcance:
mostrar TODOS los paquetes del Apartamento completo (todos los Ocupantes), no solo los propios.
Eso es una decisión de producto con implicación de privacidad (¿un Ocupante secundario debería ver
los paquetes que otro Ocupante anunció o recibió?), no solo de diseño visual — se le pregunta al
cliente antes de construir nada de este punto.

## Comments
