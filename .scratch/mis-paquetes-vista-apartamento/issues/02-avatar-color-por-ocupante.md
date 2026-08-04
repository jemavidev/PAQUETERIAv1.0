# 02 — Avatar de color por Ocupante en cada tarjeta

**What to build:** de punta a punta — en la vista ampliada de `/mis-paquetes` (ticket 01), cada
tarjeta de Paquete muestra un avatar de color junto al nombre, identificando a cuál Ocupante de la
unidad pertenece. El mismo Ocupante siempre tiene el mismo color; ningún par de Ocupantes de la
misma unidad comparte color; un Paquete cuya identidad no resuelve a ningún Ocupante conocido
muestra un avatar neutro.

**Blocked by:** 01 — Alcance ampliado: `/mis-paquetes` muestra los paquetes de todo el Apartamento.

**Status:** ready-for-agent

- [ ] Paleta fija de 5 colores, una por cada posición posible del roster de `listar_ocupantes`
      (0=principal .. 4=quinto Ocupante) — coherente con `MAX_OCUPANTES_ACTIVOS = 5` ya existente,
      no una paleta arbitraria de tamaño distinto.
- [ ] Los 5 colores de la paleta son visualmente distintos de los 4 roles semánticos ya usados
      para el estado del Paquete (ámbar/azul/verde/rojo de Anunciado/Recibido/Entregado/Cancelado)
      — un avatar de Ocupante nunca se confunde con el badge de estado de la misma tarjeta.
- [ ] Resolución de a qué Ocupante pertenece un Paquete: primero intenta matchear
      `recipient_phone` contra los Teléfonos de Ocupantes de la unidad; si no matchea, intenta
      `announced_by_phone`; si ninguno matchea, avatar neutro (mismo tono que el fallback ya
      existente de Badges).
- [ ] Un Paquete con Destinatario "nombre sin teléfono" que no corresponde a ningún Ocupante
      conocido muestra el avatar neutro, no un color inventado.
- [ ] Dos Ocupantes activos de la misma unidad nunca comparten color en la misma respuesta de
      `/mis-paquetes` — test explícito con 3+ Ocupantes activos verificando colores distintos.
- [ ] El mismo Ocupante recibe el mismo color en todas sus tarjetas dentro de la misma carga de la
      página (consistencia interna, no solo entre-Ocupantes).
- [ ] Tests nuevos en `tests/web/test_mis_paquetes.py`: match por destinatario, match por
      anunciante como respaldo, caso sin match (neutro), sin colisión de color entre Ocupantes.
- [ ] Suite completa del proyecto sigue en verde.
