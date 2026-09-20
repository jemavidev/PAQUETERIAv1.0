# 368 — `/announce`: etiqueta "Nueva persona" → "Nuevo residente"

**Pedido original (cliente):**
"Necesito que para la vista /announce cambien la etiqueta 'Nueva persona'
por 'Nuevo residente'."

**Status:** implementado

## Alcance

- El texto visible del desplegable en `/announce`, en sus dos apariciones
  (lista de residentes de una unidad y sugerencia de Contacto externo). Solo
  copy de interfaz: el comportamiento y los ganchos (`data-nueva-persona`,
  `#announce-unidad-accion`) no cambian.
- Los tickets 03 y 04 de `.scratch/contactos-externos-en-announce` siguen
  diciendo "Nueva persona": desde este issue es "Nuevo residente".

## Implementación

- El texto "Nueva persona" → "Nuevo residente" en las dos apariciones de
  `/announce` (lista de residentes de una unidad y sugerencia de Contacto
  externo), vía el componente compartido `components/
  _resumen_nuevo_residente.html` (issue 367) -- un solo lugar para las dos.
- Comentarios y docstrings de `announce_new/_identificar_unidad.html` y
  `_identificar_con_sugerencia.html` actualizados para no seguir hablando de
  "Nueva persona".
- Los ganchos (`data-nueva-persona`, `#announce-unidad-accion`) y el JS de
  `form.html` no cambiaron -- solo el copy.

## Verificación

- `tests/web/test_announce_new.py` (3 tests) y
  `tests/web/test_announce_sugerencia_contacto_externo.py` (2 tests):
  actualizados para fijar "Nuevo residente" y confirmar que "Nueva persona"
  ya no aparece.
- `tests/web/test_announce_new.py` + `test_announce_sugerencia_contacto_
  externo.py`: 121 pasan.
- Navegador a 390 px: "Nuevo residente" se ve en los dos lugares.
- Pendiente: confirmación visual del cliente y deploy a test.papyrus.com.co.
