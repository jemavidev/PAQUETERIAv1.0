# 164 — `/announce`: paquetes ANUNCIADO/RECIBIDO del residente identificado

**Pedido original:** "Necesito que en la vista de /announce, en caso que un residente tenga
paquetes anunciados a su nombre, estos se listen... presionar un botón para uno de esos paquetes e
iniciar el proceso de recepción para ese anuncio específico... identifiques con el código de
seguridad y los coloques en tipo bala... que en esta misma vista se tenga de esta forma
representados los paquetes ANUNCIADOS y RECIBIDOS, con el fin de poder desde aquí continuar su
flujo de forma más fácil."

**Status:** implementado

## Diseño (confirmado con el cliente antes de implementar)

`Paquete` no tiene FK al destinatario (ADR-0001, snapshot de texto) -- se buscan sus paquetes por
las 2 vías reales disponibles: `recipient_phone == su teléfono` (si tiene) OR
`announced_by_persona_id == su id` (FK real, cubre el caso solo-WhatsApp que se anunció a sí
mismo). Limitación conocida y aceptada: un destinatario solo-WhatsApp cuyo paquete lo anunció OTRA
persona en su nombre no queda cubierto -- no hay ningún dato que lo enlace (mitigado en parte por
[[163]], que ahora hace que `recipient_phone` intente el Teléfono del Principal más seguido).

## Cambio

- `paquete_service.paquetes_abiertos_de_persona(session, persona)`: los Paquetes ANUNCIADO/RECIBIDO
  de esa Persona, más recientes primero.
- `announce_new.py`: conectado en las 2 rutas de identificación en vivo --
  `GET /announce/identificar` (Teléfono/WhatsApp directo) y
  `GET /announce/identificar-ocupante` (residente elegido de la lista de una unidad).
- `components/_persona_resuelta.html` (`tarjeta_persona_resuelta`, compartida por los 3 puntos de
  identificación de `/announce`): nuevo parámetro `paquetes` -- si viene con algo, lista cada
  Paquete en viñetas bajo la tarjeta, con su código de acceso (misma píldora por Estado que ya usa
  `/paquetes`) y un link para continuar su flujo sin salir de `/announce`:
  - ANUNCIADO → "Recibir →", abre `/paquetes?recibir=<id>` (mecanismo YA existente).
  - RECIBIDO → "Entregar →", abre `/paquetes?entregar=<id>` (mecanismo NUEVO, ver abajo).
- `/paquetes`: nuevo query param `entregar` (`packages_list`/`_render_lista`), mismo patrón exacto
  que `ver`/`corregir`/`recibir` -- reabre el modal "Entregar" de ESE paquete puntual, sin tocar el
  modal en sí (no se reimplementó nada, solo se agregó el gancho de auto-apertura que le faltaba).

## Verificación

- 4 tests nuevos a nivel de dominio (`paquetes_abiertos_de_persona`: encuentra por teléfono,
  encuentra por FK del anunciante en el caso solo-WhatsApp, filtra entregados/cancelados, lista
  vacía sin nada).
- 6 tests nuevos a nivel de ruta (`test_announce_new.py`: ambos caminos de identificación, con
  ANUNCIADO/RECIBIDO/sin paquetes/sin contacto propio) + 2 en `test_packages.py` (el nuevo query
  param `entregar` abre y no-abre el modal correctamente).
- Suite completa: 1059/1059.
- Verificado en vivo contra `localhost:8010`: anunciado un paquete de prueba, confirmado que
  aparece en `/announce/identificar` con su código y el link "Recibir →"; recibido, confirmado que
  el link cambia a "Entregar →" y abre el modal correcto; entregado, confirmado que desaparece de
  la lista.
