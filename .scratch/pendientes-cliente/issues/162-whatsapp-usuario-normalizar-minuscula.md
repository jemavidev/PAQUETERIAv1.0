# 162 — Usuario de WhatsApp se normaliza a minúscula

**Pedido original:** pregunta ("para los usuarios de WhatsApp se requiere que sean mayúsculas o
minúsculas?") seguida de instrucción explícita: "con relación a lo de usuarios de whatsapp,
normalizalo a como lo requiere META/WhatsApp para identificar a sus diferentes usuarios."

**Status:** verificado

## Diagnóstico

`WHATSAPP_USUARIO_RE` acepta mayúsculas y minúsculas por igual, pero el sistema NUNCA
normalizaba el case -- se guardaba y se comparaba tal cual se tecleó (`Persona.whatsapp_usuario
== whatsapp_usuario`, comparación exacta, sensible a mayúsculas). Meta identifica un usuario de
WhatsApp SIN distinguir mayúsculas de minúsculas -- `Jesus.Villalobos` y `jesus.villalobos` son
la MISMA cuenta para WhatsApp, pero el sistema los trataba como dos contactos distintos.

## Cambio

- Nueva función `_normalizar_whatsapp_usuario` (`persona_service.py`): recorta espacios, quita el
  `@` inicial, y pasa a minúscula -- una sola fuente de verdad, mismo patrón que
  `normalizar_telefono` para Teléfono.
- Conectada en los 3 puntos que leen/escriben este campo: `get_or_create_persona_por_whatsapp`,
  `buscar_persona_por_whatsapp`, `update_datos_personales`. El resto de la app (`agregar_ocupante`,
  `ocupante_activo_por_contacto`, etc.) ya pasa por estas 3 funciones -- ningún otro caller
  necesitó cambios.
- Migración `0029_whatsapp_usuario_minuscula` (mismo espíritu que `0017_normalizar_casing_
  nombres`): backfill de `personas.whatsapp_usuario` existente a minúscula, idempotente. Sin
  manejo especial de colisión a propósito -- si dos Personas YA distintas terminaran con el mismo
  usuario en minúscula, el índice único parcial rechaza el UPDATE en seco (sería una fusión de
  Personas aparte, no algo para resolver en silencio).
  - Bug real encontrado en el camino: el primer intento de nombre de revisión
    (`0029_normalizar_whatsapp_usuario_minuscula`, 42 caracteres) reventó la migración --
    `alembic_version.version_num` es `VARCHAR(32)`. Se acortó a `0029_whatsapp_usuario_minuscula`
    (31 caracteres).

## Verificación

- 1 test nuevo (`test_whatsapp_usuario_guarda_en_minuscula`).
- Suite completa: 1047/1047.
- Verificado en vivo contra `localhost:8010`: los 4 residentes con WhatsApp ya registrado
  (mezcla de mayúscula/minúscula) quedaron en minúscula tras la migración; búsquedas con
  capitalización distinta a la guardada (`JesusMariaVillalobos`, `JESUSMARIAVILLALOBOS`) resuelven
  igual al mismo residente.
