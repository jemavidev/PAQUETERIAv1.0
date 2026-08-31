# 261 — Email pasa a semántica de 3 estados (dejarlo vacío lo borra), igual que WhatsApp

**Pedido original (cliente):** "Sí, dale el mismo tratamiento de 3
estados a Email" — confirmando el diagnóstico: hoy dejar el campo Email
vacío y guardar NO lo borra (se interpreta como "no tocar", mismo bug
que `whatsapp_usuario` tenía antes de issue 69), porque `_blank_to_none`
convierte "" a `None` antes de llegar a `update_datos_personales`, y esa
función trata `email=None` como "no tocar" (contrato de 2 estados).

**Status:** implementado

## Alcance

`persona_service.update_datos_personales`: extender a `email` el mismo
contrato de 3 estados que ya tiene `whatsapp_usuario` -- `None` = no
tocar; `""` explícito = BORRARLO (`persona.email = None`); no vacío = se
valida el formato y se guarda. Nombre se queda en 2 estados (una Persona
siempre necesita nombre, no aplica "borrarlo").

4 call sites de `update_datos_personales` pasan `email=`, los 4 hoy
colapsan "" a `None` con `_blank_to_none` ANTES de llamar -- hay que
dejar de hacerlo para email específicamente (nombre se queda igual) para
que la señal de "vacío explícito" llegue:

- `customers_manage.py` tab "Datos" (staff, ficha propia) -- línea ~632.
- `customers_manage.py` modal "Editar" del roster (staff, tab
  Residentes, issue 251) -- línea ~1146/1167.
- `customer_verify.py` tab "Datos" (autoservicio, `/mis-datos`) --
  línea ~293.
- `customer_verify.py` modal "Editar" del roster (autoservicio, issue
  228) -- línea ~622/644.

Los 4 formularios ya mandan siempre el campo `email` (es un `<input>`
de texto normal, no un checkbox) -- mismo requisito que ya cumple
WhatsApp en esos mismos 4 lugares.

## Implementación

- `persona_service.update_datos_personales`: `email` pasa a 3 estados,
  mismo criterio que `whatsapp_usuario` (`None` no toca, `""` borra,
  valor no vacío se valida y guarda). Validación de formato salteada
  para `""` a propósito.
- Los 4 call sites dejaron de colapsar `""` a `None` con `_blank_to_none`
  para `email` (nombre se queda igual, 2 estados).

**Bug real encontrado al implementar** (via diagnosing-bugs, feedback
loop = test que falló): en la ruta staff del modal Editar
(`customers_manage_ocupante_editar`), un primer intento usó `email_v =
(email or "").strip() if email is not None else None` para distinguir
"campo ausente" de "campo vacío" -- pero esa ruta lee `email` vía
`email: str = Form(None)` (inyección de FastAPI), y **FastAPI ya
colapsa un `""` enviado a `None`** antes de que el body de la ruta lo
vea (confirmado con un repro mínimo aislado, sin nada de este proyecto
de por medio) -- la misma colisión que hace que "ausente" y "vacío" ya
sean indistinguibles a esta altura, así que el chequeo `is not None`
era código muerto que siempre tomaba la rama "no tocar". Las rutas de
`/mis-datos` (customer_verify.py) NO tienen este problema porque leen
el form crudo via `await request.form()` (Starlette conserva `""` sin
colapsar), no vía `Form()`. Fix: usar el mismo idiom `(email or
"").strip()` sin el chequeo `is not None`, igual que ya hacía
`whatsapp_v` en esa misma ruta (por eso WhatsApp nunca mostró este bug).

## Verificación

- Tests nuevos: `test_email_string_vacio_lo_borra`,
  `test_email_none_no_lo_toca`,
  `test_email_invalido_rechaza_pero_vacio_no_valida_formato`
  (`test_persona_service.py`); `test_staff_borra_el_email_ya_seteado`,
  `test_staff_edita_ocupante_unificado_email_vacio_lo_borra`
  (`test_customers_manage.py`); `test_email_vacio_en_mis_datos_lo_borra`,
  `test_editar_ocupante_unificado_email_vacio_lo_borra`
  (`test_customer_verify.py`) -- cubren los 4 call sites.
- Suite completa (`tests/web` + `tests/data_model`): 1245 passed.
