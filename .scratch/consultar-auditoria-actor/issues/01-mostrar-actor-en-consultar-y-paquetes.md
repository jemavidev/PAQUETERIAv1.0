# Ticket 01 — Mostrar actor de cada transición en /consultar y /paquetes

**Spec:** `.scratch/consultar-auditoria-actor/spec.md`
**Status:** todo

## Alcance

- [ ] `app/domain/actor_service.py` nuevo: `nombre_usuario(session, usuario_id) -> str | None`.
- [ ] `search.py`: `_timeline` agrega `actor` por hito (staff con etiqueta
      "(staff)"; anunciante-cliente con etiqueta "(cliente)"; `None` si no
      hay actor).
- [ ] `search/form.html`: renderiza el actor bajo cada hito de la línea de
      tiempo, si existe.
- [ ] `packages.py` (`_listar`): cada `Paquete` gana
      `p.actor_ultima_accion` (Cancelado > Entregado > Recibido > Anunciado).
- [ ] `packages/list.html`: renderiza `p.actor_ultima_accion` en la tarjeta.
- [ ] Actualizar el docstring de `search.py` (ya no es cierto que "sin
      exponer al operador").

## Tests (TDD, antes del código)

- [ ] `/consultar` de un paquete anunciado por el propio cliente muestra su
      nombre con "(cliente)".
- [ ] `/consultar` de un paquete anunciado por staff (vía `/announce`)
      muestra el nombre del `Usuario` con "(staff)".
- [ ] `/consultar` de un paquete Recibido/Entregado/Cancelado muestra el
      nombre del `Usuario` que hizo cada transición.
- [ ] `/paquetes`: la tarjeta de un paquete Cancelado muestra el actor de la
      cancelación, no el de recepción (prioridad correcta).
- [ ] `/paquetes`: la tarjeta de un paquete recién Anunciado (sin más
      transiciones) muestra el actor del anuncio.
