# 307 — Torre/Apto en rojo y sin link cuando el destinatario ya se mudó (paquetes cerrados)

**Pedido original (cliente):** caso real encontrado con el paquete "9CA5" (ENTREGADO, destinatario
TOMAS LIBANO): el modal "Ver" muestra "Torre 10 · Apt 302" como link azul clickeable hacia la ficha
del residente, pero Tomás ya no vive ahí (se mudó de vuelta a Torre 5 · 302) -- el link lleva a una
ficha que muestra una dirección distinta a la que el propio modal está mostrando. Pide: cuando el
destinatario resuelto de un paquete YA CERRADO (ENTREGADO/CANCELADO) ya no vive en la unidad
congelada en el snapshot, el texto "Torre X · Apt Y" debe verse en **rojo** y dejar de ser un link
-- tanto en el modal "Ver" como en la columna "Dirección" de la tabla.

**Status:** implementado -- pendiente verificar visualmente en vivo.

## Diagnóstico

Ya existía una detección PARCIAL de este caso: `cambios_recientes_de_apartamento`
(`ocupante_service.py`, issue 165) pinta un ícono 🔄 con tooltip "Vivía antes en..." -- pero SOLO si
el cambio fue en los últimos 30 días, y no evita el click ni cambia el color. Para paquetes
ANUNCIADO/RECIBIDO (abiertos) esto ya estaba cubierto de otra forma: si el destinatario se mudó, deja
de ser Ocupante activo de esa unidad y el sistema ya lo trata como "no confirmado" (advertencia
naranja, sin link) -- `destinatario_coincide_con_candidato_real` exige que sea un Ocupante REAL y
ACTIVO de la unidad del snapshot. El gap real es SOLO en paquetes ya CERRADOS: ahí la confirmación es
histórica (`corrected_at`), nunca se revalida contra la ocupación actual.

Pedido explícito del cliente, confirmado: (1) el ícono 🔄 se RETIRA por completo (reemplazado por el
color, sin límite de 30 días); (2) la misma lógica aplica también a la columna "Dirección" de la
tabla, no solo al modal.

## Qué se hizo

- Nuevo atributo transitorio `p.destinatario_se_mudo` (`_listar()`, `packages.py`) -- `True` solo
  cuando el paquete está en ENTREGADO/CANCELADO, el destinatario resuelve a una Persona real
  (`persona_destino`), y su apartamento ACTUAL (`Persona.apartamento_actual_id`) es distinto del
  apartamento resuelto del snapshot del paquete.
- Retirado el consumo de `cambios_recientes_de_apartamento`/`p.cambio_reciente_apartamento` de
  `packages.py` y el ícono 🔄 de ambos lugares (`_resultados.html`) -- el servicio de dominio
  (`ocupante_service.cambios_recientes_de_apartamento`) y sus propios tests NO se tocaron (siguen
  siendo código de dominio genérico y testeado, aunque hoy se quede sin caller).
- Tabla ("Dirección"): con `destinatario_se_mudo`, el texto pasa a `text-red-600` (antes
  `text-slate-700`).
- Modal "Ver": con `destinatario_se_mudo`, el Torre/Apto queda como `<span>` en rojo (sin link),
  en vez del `<a>` azul de siempre -- ya no depende de si `persona_destino_id`/`advertencia_nombre`
  habilitarían el link, porque ese caso ahora tiene prioridad sobre esa decisión.
