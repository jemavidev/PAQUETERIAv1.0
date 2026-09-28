# 429 — Mensajes de confirmación que nunca se mostraban

**Origen:** análisis de enlaces, hallazgo 2. Jesús: "corrige los 3 problemas que encontraste".

**Status:** verificado (`a3bda27`, confirmado por Jesús en test 2026-09-28)

## Contexto

Tres redirecciones agregan un parámetro que ninguna vista leía:

- `/otp?telefono_actualizado=1`: el residente cambia su teléfono en `/mis-datos`, se le cierra la sesión y cae en
  "Verificar mi teléfono" sin explicación.
- `/otp?cuenta_eliminada=1`: tras eliminar su cuenta, la misma pantalla sin confirmación.
- `/residentes?eliminado=1`: el staff elimina un residente y la lista no dice nada.

## Decisiones

- `/otp` muestra un toast según el parámetro: "Tu teléfono se actualizó. Verifica el número nuevo para volver a
  entrar." / "Tu cuenta fue eliminada."
- `/residentes` muestra "Residente eliminado." (mismo estilo que el "Motivo eliminado." de administración).

## Verificación

- `tests/web/test_mensajes_tras_redireccion.py` (3 de 4 fallaban antes; la cuarta confirma que sin parámetro no sale
  ningún aviso). Afectadas + infra: 347 en verde. Sin clases de Tailwind nuevas (`toast` existente).
