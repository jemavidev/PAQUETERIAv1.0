# 11 — Gate "cliente verificado" en `/mis-datos`

**What to build:** una Persona nace con nombre+teléfono (vía `/anunciar` o `/otp`) y puede recibir paquetes, anunciar, etc. desde el primer momento — pero NO puede ver ni editar `/mis-datos` hasta que se le haya recibido físicamente al menos un paquete a su nombre. Control anti-abuso: `/anunciar` no verifica nada hoy (cualquiera crea una Persona con un teléfono+nombre inventado); sin este gate, alguien podría usar `/otp` para entrar a `/mis-datos` con un teléfono nunca verificado por un humano.

Nueva función `es_cliente_verificado(session, persona)`: existe algún `Paquete` cuyo destinatario resuelto (misma lógica que `notificacion_service.resolver_destino`: `recipient_phone`, o si no tiene, `announced_by_phone`) sea el teléfono de esta Persona, Y que ese Paquete haya llegado a `RECIBIDO` en algún momento (`received_at is not None` — aunque después haya pasado a Entregado/Cancelado, sigue contando). **Calculado al vuelo, nunca un campo guardado.**

El chequeo se hace SOLO en la ruta `/mis-datos` (GET y POST), como comprobación adicional junto a `current_customer` — **nunca en `/otp/solicitar` ni `/otp/verificar`** (bloquear ahí permitiría enumerar por mensaje de error qué teléfonos son clientes reales). Cualquiera sigue pudiendo pedir/verificar su OTP con normalidad.

Sin el gate, en vez del formulario se muestra una pantalla simple: "Tu cuenta se activa por completo cuando te recibamos tu primer paquete — mientras tanto podés seguir anunciando normalmente", sin exponer ni permitir editar nada.

**Blocked by:** Ninguno — puede empezar de inmediato, independiente del sistema de Ocupantes.

**Status:** done

- [x] `es_cliente_verificado(session, persona)` calculada al vuelo, reutilizando la lógica de `resolver_destino`.
- [x] Una Persona sin ningún paquete que haya llegado a Recibido a su nombre (y sin ser Ocupante activo de nada), al entrar a `/mis-datos`, ve la pantalla informativa en vez del formulario.
- [x] Una Persona con al menos un paquete que llegó a Recibido (incluso si después pasó a Entregado o Cancelado) accede con normalidad.
- [x] El flujo de `/otp/solicitar` y `/otp/verificar` en sí no cambia (ningún chequeo NUEVO en esas rutas) — pero ver la corrección abajo.
- [x] Tests cubren: sin paquete recibido bloquea; con paquete recibido (incluso ya Entregado/Cancelado) permite acceso; ser Ocupante activo también verifica.

## Ampliación de alcance descubierta durante la implementación

`es_cliente_verificado` también es `True` si la Persona ya es Ocupante ACTIVO
de algún Apartamento (no solo por paquete recibido) — quedó ahí por una
acción humana explícita (el principal, ya verificado, lo agregó; o el staff
directamente), no por autoservicio sin verificar. Sin esto, un segundo
contacto recién creado por el principal (ticket 03) jamás podría pasar el
gate para usar su propia sesión (ticket 05).

**Corrección relacionada, más profunda:** se descubrió que `otp_service.
elegible_para_otp` (el gate que decide si se envía un código OTP) exigía
Paquete en RECIBIDO — un segundo contacto recién agregado, sin ningún
Paquete propio, ni siquiera podía RECIBIR un código para loguearse, dejando
el ticket 05 completo inalcanzable en la práctica. Corregido: `elegible_para_
otp` ahora también acepta "ya es Ocupante activo de algún Apartamento" como
vía de elegibilidad alternativa. 3 tests nuevos en `test_otp_service.py`.

## Implementación

- `notificacion_service.es_cliente_verificado` (nuevo).
- `customer_verify.py`: `_gate_no_verificado` aplicado a las 8 rutas de `/mis-datos*` (GET, POST, y las 6 de gestión/autoservicio de Ocupantes). Plantilla nueva `customer/no_verificado.html`.
- `otp_service.elegible_para_otp` ampliado (ver arriba).
- 5 tests nuevos en `test_notificacion_service.py` + 2 en `test_otp_service.py`. Suite completa: 519 passed.
- Nota: no hay test a nivel web del gate "bloqueando" — dado el estado actual del código, es estructuralmente imposible obtener una sesión de cliente (siempre pasa por `/otp/verificar`, que ya exige elegibilidad) sin que `es_cliente_verificado` también sea `True`. El gate queda como defensa en profundidad, verificado exhaustivamente a nivel de dominio.
