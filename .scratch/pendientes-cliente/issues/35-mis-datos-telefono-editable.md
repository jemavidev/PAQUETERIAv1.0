# 35 — `/mis-datos`: el teléfono de cualquier contacto debe ser editable

**Pedido original (cliente):** "El numero de telefono del cualquiera de los
contactos debe ser editable."

**Status:** verificado

## Decisión del cliente

Si el PRINCIPAL edita su propio teléfono: se guarda, se cierra la sesión, y
se le exige verificar de nuevo por OTP al número nuevo (confirma que de
verdad lo controla, no solo que lo escribió).

## Implementación

- `persona_service.cambiar_telefono_propio(session, persona, nuevo_telefono)`
  (nuevo) — renombra la fila de Persona existente (mismo id, mismo
  historial); rechaza si el número ya pertenece a otra Persona.
- `ocupante_service.editar_telefono_ocupante(session, ocupante, nuevo_telefono)`
  (nuevo) — re-liga `persona_id` a la Persona del nuevo teléfono; rechaza
  sobre el principal (usa el mecanismo de arriba) y sobre un Ocupante sin
  teléfono todavía (usar "Asociar").
- `customer_verify.py`: campo `telefono` nuevo en "Datos personales"
  (procesado AL FINAL del POST, después de todo lo demás); si cambia, cierra
  sesión y redirige a `/otp`. La ruta `POST /mis-datos/ocupantes/{id}/telefono`
  ahora rama entre `asociar_telefono_a_ocupante` (sin teléfono previo) y
  `editar_telefono_ocupante` (ya tenía uno) — mismo formulario para ambos.
- `customers_manage.py` (staff): misma rama en su ruta equivalente. Staff NO
  tiene hoy una vía para editar el teléfono PROPIO de un principal (mismo
  estado que antes de este pedido, sin regresión).
- Templates: input editable de Teléfono en `/mis-datos` (Datos personales) e
  input "Guardar teléfono" junto a cada Ocupante con teléfono, en
  `/mis-datos` y en `/residentes/{id}` (staff).
- Tests: 4 de dominio (`test_persona_service.py`), 4 de dominio
  (`test_ocupante_service.py`), 4 web cliente (`test_customer_verify.py`), 1
  web staff (`test_customers_manage.py`).
