# 38 — `/mis-datos`: error de "dar de baja" aparece al intentar otro cambio

**Pedido original (cliente):** "Necesito que intentes probar cada aspecto de
los formularios en esta vista, ya que trate de hacer unos cambios y no me lo
permitio, indica este error 'El principal no puede darse de baja mientras
existan otros Ocupantes activos -- promové a alguno primero, o dales de baja
a todos antes de darte de baja tú.' que no hace referencia a lo que queria
cambiar en si."

**Status:** verificado

## Diagnóstico (`diagnosing-bugs`)

No era un bug de lógica: el bloqueo es correcto y a propósito (spec §2-3, un
principal no puede "mudarse" de Torre/Apartamento dejando otros Ocupantes
activos dependiendo de él, sin resolverlo primero). Reproducido con un test:
un principal con al menos un Ocupante activo que intenta cambiar Torre o
Apartamento a un valor DISTINTO (aunque sea corregir un typo) dispara la
rama de auto-baja-antes-de-mudar en `customer_verify.py`, que hasta ahora
dejaba pasar tal cual el mensaje de `dar_de_baja_ocupante` ("no puede darte
de baja...") — un concepto que quien solo quería corregir su Apartamento
nunca invocó a propósito. Descartadas por reproducción real: reenviar el
mismo apartamento sin cambios, editar nombre/email/notificaciones con otros
Ocupantes activos -- ninguno dispara el mensaje (la guardia de idempotencia
funciona bien).

## Implementación

`customer_verify.py`: ese `except ValueError` específico ahora devuelve un
mensaje propio ("No puedes cambiar de Torre/Apartamento mientras tengas
otros Ocupantes activos en tu unidad actual -- promueve a alguno como
principal primero, o dales de baja a todos antes de mudarte."), marcado en
los campos `torre`/`apartamento`. El mensaje original de
`dar_de_baja_ocupante` se sigue usando tal cual en los botones "Dar de baja"
y "Salir de este apartamento", donde sí es la intención directa del clic.

Test nuevo `test_cambiar_apartamento_con_dependientes_da_mensaje_claro`
confirma el mensaje nuevo y la ausencia del texto viejo ("darte de baja") en
ese caso.
