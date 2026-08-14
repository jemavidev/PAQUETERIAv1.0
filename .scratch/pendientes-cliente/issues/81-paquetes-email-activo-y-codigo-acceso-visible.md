# 81 — `/paquetes`: ícono Email corregido + código de acceso visible para staff

**Pedido original (cliente):**
1. "Veo que la columna de Acciones el icono de email no esta activo donde
   debe estar, analiza ya que algunos usuarios, por ejemplo los que tienen
   paquetes anunciados y tienen correo deberian no estar desactivados o en
   gris, analiza" — bug: el ícono Email de Acciones quedó codeado para
   estar SIEMPRE apagado (issue 79), sin usar el dato que sí existe
   (`Persona.email` del Anunciante, el mismo que ya mostraba el modal
   "Ver").
2. "hay algo que no veo en el modal de clientes, deberia ser posible ver el
   codigo de acceso, o mejor aun en su defecto este codigo de acceso debera
   estar visible en la misma columna de clientes al lado del nombre del
   cliente al igual que dentro del modal al lado del boton para cambiar de
   estado Recibir o Entregar."

**Status:** implementado

## Contexto

Punto 2 revierte una regla de negocio EXPLÍCITA y probada
(`test_packages_con_sesion_lista_y_muestra_estado`, agregada 2026-07-30):
"el código de acceso es el secreto que el cliente usa en `/consultar`, no
algo para exponer en una lista compartida". Antes de implementar se le
preguntó al cliente directamente si confirmaba mostrarlo sabiendo que
cualquiera que vea la pantalla del staff podría verlo — confirmó
explícitamente: "Solo mostrar pero para el personal de Staff, los clientes
continuan igual". `/paquetes` ya es 100% staff-only (`current_staff`), así
que esto no cambia nada para el cliente en `/consultar` ni `/mis-paquetes`.

## Implementación

- `packages/_acciones.html`: el ícono Email deja de estar codeado a
  SIEMPRE apagado -- ahora usa `p.persona_anunciante.email` (mismo dato que
  ya mostraba el modal "Ver", `announced_by_persona_id` es NOT NULL así que
  `persona_anunciante` siempre existe). Color activo `indigo-600` (distinto
  de WhatsApp/Teléfono para no confundirse). `title`/`aria-label` aclaran
  que es el email de quien anunció, no necesariamente el destinatario (solo
  coincide en el caso "yo mismo").
- `packages/_resultados.html`:
  - Columna Cliente: `p.access_code` como texto chico gris junto al nombre.
  - Modal "Ver": `p.access_code` en fuente monoespaciada junto al ícono de
    siguiente estado (Recibir/Entregar) en la esquina superior derecha,
    visible también en Entregado/Cancelado (el código no depende del
    estado, aunque ahí no hay ícono de acción al lado).
- `tests/web/test_packages.py`:
  - `test_packages_con_sesion_lista_y_muestra_estado`: assertion invertida
    (`access_code in r.text`, ya no `not in`).
  - 2 tests nuevos para el ícono Email (activo con email del anunciante,
    apagado sin él).

## Verificación

- `tests/web/` completo: 483 tests pasan.
- Verificación manual en navegador: ícono Email en indigo con datos reales,
  código de acceso visible en la columna Cliente y en el modal "Ver" junto
  al ícono de acción.
- Desplegado 2026-08-15 junto con [[80]] (mismo push a `jemavidev/PaqueteX`,
  ver esa nota de despliegue). Pendiente confirmar visualmente en vivo.
