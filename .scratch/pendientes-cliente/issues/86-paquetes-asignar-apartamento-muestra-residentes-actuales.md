# 86 — `/paquetes` "Asignar apartamento": muestra si la unidad está libre o tiene residentes

**Pedido original (cliente):**
"hagamos algo ahora, para cuando se digite el apartamento, deberia
aparecer si este esta libre o si tiene residentes actuales, esto con el
fin de saber si se asocia o no un usuario sin apartamento a otro"

**Status:** implementado

## Contexto

Sobre el buscador de unidad de [[85]]: antes de asociar un paquete
"Sin apartamento" a una unidad del catálogo, el staff no tenía forma de
saber si esa unidad ya tenía residentes -- riesgo real de mezclar por
error a alguien con una familia que no es la suya.

## Implementación

- `domain/ocupante_service.py`: función nueva
  `residentes_por_torre_apartamento(session)` -- `{torre: {apartamento:
  [nombre, ...]}}`, SOLO unidades con al menos un Ocupante ACTIVO, en una
  sola consulta (join Apartamento+Ocupante) para todo el catálogo. Una
  unidad ausente del dict está libre.
- `routes/packages.py`: se computa una vez por página (`_render_lista`,
  mismo criterio que `catalogo_torres`) y se pasa al contexto como
  `residentes_por_unidad`.
- `packages/_resultados.html`, modal "Asignar apartamento": cada
  resultado de búsqueda ahora muestra, a la derecha del nombre de la
  unidad, un chip -- **"Libre"** (verde) si no tiene residentes, o el
  primer nombre + "+N" (naranja, con `title` mostrando todos los
  nombres) si ya los tiene. Los datos viajan igual que el catálogo: un
  `<script type="application/json">` por paquete, consumido por el mismo
  JS de búsqueda ya existente.

## Tests

- `test_residentes_por_torre_apartamento_solo_unidades_con_ocupante_activo`
  (dominio): confirma que un Ocupante dado de baja no cuenta, y que una
  unidad nunca tocada está ausente del dict.
- `test_modal_asignar_apartamento_expone_residentes_por_unidad` (web):
  confirma el JSON servido en el modal real vía HTTP.

## Verificación

- `tests/` completo: 922 tests pasan.
- Verificación manual vía HTTP (ambiente local): el script
  `residentes-unidad-asignar-<id>` sirve datos reales (confirmado con la
  simulación de familias ya cargada en local).
- Pendiente: deploy a test.papyrus.com.co.
