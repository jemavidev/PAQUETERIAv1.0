# 332 — Quitar la advertencia naranja "destinatario no coincide" de /paquetes

**Pedido original (cliente):** "necesito que esta seccion no aparezca en ninguna de las vistas 'El
destinatario todavía no coincide con ningún residente registrado', esto ya no es necesario."

**Status:** implementado, pendiente desplegar a test.papyrus.com.co y que el cliente lo confirme.

## Decisión de alcance (confirmada con el cliente antes de implementar)

El mensaje es el título/tooltip del ícono de alerta naranja que hoy aparece en 2 lugares de
`/paquetes` cuando `p.advertencia_nombre` es verdadero (el nombre del destinatario todavía no
coincide con ningún residente confirmado):
1. Junto al nombre del destinatario, columna "Cliente".
2. Botón grande dentro del modal "Ver".

Ambos son, además, puntos de entrada al modal "Corregir destinatario". Un TERCER punto de entrada
al mismo modal ya existe, independiente de `advertencia_nombre`: el ícono "Modificar" (lápiz gris,
`packages/_acciones.html`, columna Acciones) -- gateado solo por `estado` (ANUNCIADO/RECIBIDO), no
por la advertencia. Se confirmó con el cliente: quitar SOLO la advertencia visual, dejando
"Corregir destinatario" accesible vía "Modificar" -- no se toca el backend (`POST /paquetes/{id}/
corregir`) ni el modal en sí, que ya no está gateado por `advertencia_nombre` en ningún punto.

`p.advertencia_nombre` (la variable) NO se retira -- sigue gateando otro comportamiento sin
relación con esta advertencia visual (si se muestra el link de Torre/Apto, si se muestra la lista
de `residentes_unidad`). Tampoco se toca `p.destinatario_eliminado` (ícono rojo "cuenta eliminada"
-- mensaje y caso de uso distintos, el cliente no lo mencionó).

## Implementación

- `app/web/templates/packages/_resultados.html`:
  - Columna "Cliente": se retiró el bloque `{%- elif p.advertencia_nombre %}` completo (ícono
    naranja clickeable para ANUNCIADO/RECIBIDO + ícono naranja estático para el resto) -- el bloque
    `{%- if p.destinatario_eliminado %}` (ícono rojo) queda intacto.
  - Modal "Ver": se retiró el botón redondo naranja `data-open="modal-correct-{{ p.id }}"` (con el
    mismo tooltip) que aparecía cuando `p.advertencia_nombre and p.estado.value in ("ANUNCIADO",
    "RECIBIDO")`.

## Verificación

- 4 tests que asumían la advertencia visual se ajustaron a la nueva realidad (2 invertidos para
  confirmar que YA NO aparece, incluso con mismatch; 2 borrados por quedar redundantes/obsoletos --
  el que probaba el botón dentro de "Ver" que se retiró, y el de "no clickeable en Cancelado", ya
  cubierto por `test_boton_corregir_aparece_en_anunciado_y_recibido_no_en_entregado_ni_cancelado`).
  Suite completa `tests/web/test_packages.py`: 230/230 en verde.
- Verificado en vivo (navegador, ambiente local): con el paquete real `52HE` (destinatario
  "Daniela Arrazola" con el teléfono de Angelica, caso genuino de mismatch presente en la BD de
  dev) -- confirmado que ya no aparece el ícono/tooltip naranja ni en la columna Cliente ni dentro
  del modal "Ver".
