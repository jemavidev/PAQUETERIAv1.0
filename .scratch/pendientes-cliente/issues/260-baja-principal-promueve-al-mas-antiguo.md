# 260 — `/residentes` ❌ Eliminar sobre el Principal: promueve automáticamente al más antiguo

**Pedido original (cliente):** "sí, implementa siguiendo el patrón de
mover_ocupante" — confirmando la propuesta de reusar el mismo mecanismo
de auto-promoción que ya existe en `mover_ocupante` (issue 159) para el
flujo "Mudarse de este apartamento".

**Status:** implementado

## Alcance (ajustado tras revisión de scope)

El plan original proponía cambiar `ocupante_service.dar_de_baja_ocupante`
directamente. Al revisar los llamadores se encontró que esa función es
COMPARTIDA: además de `/residentes/.../baja` (staff), también la usa el
autoservicio del cliente (`/mis-datos/ocupantes/salir` y
`/mis-datos/ocupantes/{id}/baja`, `customer_verify.py`), cuyo docstring
documenta a propósito la restricción actual ("cualquiera puede darse de
baja a sí mismo, sea principal -solo si es el último activo- o no").

Se preguntó al cliente si la auto-promoción debía aplicar también al
autoservicio o solo a staff -- respuesta: **solo staff**, igual que
`mover_ocupante` ya es "acción exclusiva de staff" (nunca autoservicio).

## Implementación

- `ocupante_service.dar_de_baja_ocupante`: **sin cambios de comportamiento**
  -- mantiene su guard estricto (rechaza con `ValueError` si el Principal
  tiene otros Ocupantes activos), documentado en su docstring como
  intencional para el autoservicio del cliente.
- `customers_manage.py::customers_manage_ocupante_dar_de_baja` (ruta
  `/residentes/{persona_id}/ocupantes/{ocupante_id}/baja`, exclusiva de
  staff): antes de llamar a `dar_de_baja_ocupante`, si `ocupante` es
  Principal, busca al Ocupante activo con `persona_id` no nulo más
  antiguo (`created_at` ascendente, mismo criterio/orden que
  `mover_ocupante`) y lo promueve (`promover_a_principal`, que degrada a
  `ocupante` en el mismo acto) -- para cuando `dar_de_baja_ocupante` corre,
  `ocupante` ya no es Principal, así que su guard nunca se dispara en
  este camino.
  - Si hay otros Ocupantes activos pero NINGUNO tiene Teléfono ni
    WhatsApp propio para sucederlo: mensaje de error específico (mismo
    criterio que `mover_ocupante`), en vez de dejar caer el mensaje
    genérico de autoservicio ("...antes de darte de baja tú", que no
    calzaba en boca de staff).
- Sin modal nuevo ni texto de aviso adicional en `/residentes` -- mismo
  criterio "silencioso" que ya usa `mover_ocupante`/"Mudarse de este
  apartamento" (verificado: ese modal tampoco avisa de la promoción).

## Verificación

- Tests nuevos en `test_customers_manage.py`:
  `test_staff_elimina_al_principal_promueve_automaticamente_al_mas_antiguo`
  (con 2 candidatos, confirma que se promueve al más antiguo por
  `created_at`, no al otro) y
  `test_staff_elimina_al_principal_sin_sucesor_con_contacto_rechaza`
  (rechaza sin mutar nada si nadie más tiene contacto propio). Suite
  completa (`test_customers_manage.py` + `test_ocupante_service.py`):
  260 passed.
- Verificado en vivo contra el dev local con datos descartables (unidad
  vacía TORRE 1 apto 101, 3 Ocupantes sintéticos creados y borrados
  después de la prueba): POST real a `.../baja` sobre el principal ->
  303, el más antiguo de los dos restantes quedó `es_principal=True`, el
  otro sin tocar, el principal original quedó `desvinculado_en` con
  fecha y `es_principal=False`.
