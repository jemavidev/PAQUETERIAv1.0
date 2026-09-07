# 329 — `/announce`: badge con paquetes ANUNCIADO por residente en la lista de la unidad

**Pedido original (cliente):** "Sería bueno ver en los residentes el número de paquetes que tiene
cada uno anunciado, colócalo con un badge."

**Status:** implementado, pendiente desplegar a test.papyrus.com.co y que el cliente lo confirme.

## Diseño

Reusa el color fucsia del pill de "total de paquetes" que ya existe en `/residentes` (issue 321),
pero acotado a `ANUNCIADO` -- mismo conteo que ya calcula `_paquetes_en_curso` (issue 325) para no
divergir. Un residente sin Persona propia (pending, sin contacto) no puede ser destinatario de
ningún Paquete todavía, así que no entra al diccionario (sin badge, no "0").

## Implementación

- `app/web/routes/announce_new.py`: `_conteo_anunciados_por_ocupante(session, residentes) ->
  {ocupante_id: cantidad}` -- una query por residente (aceptable, tamaño real de una unidad).
  Cableado en los 2 call-sites que renderizan `_identificar_unidad.html` (co-residentes y
  torre+apto directo).
- `app/web/templates/announce_new/_identificar_unidad.html`: badge fucsia (`<span>`, no `<a>` --
  el botón del residente ya es interactivo, un link anidado sería HTML inválido) junto al nombre,
  con `title` describiendo la cantidad.

## Verificación

- 2 tests nuevos en `tests/web/test_announce_new.py` (conteo singular y plural, más un residente
  sin paquetes que no muestra badge).
