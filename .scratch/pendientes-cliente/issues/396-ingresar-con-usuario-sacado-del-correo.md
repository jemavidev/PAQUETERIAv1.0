# 396 — Ingreso del staff con usuario, además del correo (usuario = lo que va antes de la "@")

**Pedido original (Jesús):** "es posible que paralelo a el email se pueda también ingresar con un nombre de usuario ...
(email: jveyes@gmail.com, entonces usuario: jveyes)" -- tras el análisis: "sí, hazlo con el usuario sacado del correo".

**Status:** implementado, pendiente confirmar en vivo (localhost)

## Decisiones

- El usuario NO se guarda: se deriva del correo (`jveyes@gmail.com` → `jveyes`). Sin columna nueva ni migración; todo
  el staff lo tiene desde ya. Sin distinguir mayúsculas.
- `/ingresar`: el campo pasa a "Email o usuario" (texto, no `type="email"`, que rechazaría "jveyes"). Con "@" se busca
  por correo como siempre; sin "@", por el usuario. Mismo mensaje genérico de error, mismo límite de intentos.
- Sin ambigüedad: al crear personal se rechaza un correo cuyo usuario ya use otra cuenta. Si aun así hubiera dos
  cuentas con el mismo usuario (creadas antes), ese usuario no entra con el nombre corto -- solo con el correo.
- Sin cambios: recuperar contraseña sigue siendo por correo; el correo de una cuenta no se edita después de creada.

## Verificación

- `tests/web/test_ingresar_con_usuario.py` (8; 4 fallaban antes): usuario, mayúsculas, correo completo, error genérico, formulario sin `type="email"`, crear personal con usuario repetido rechazado, dos cuentas viejas con el mismo usuario -> solo entran por correo. Suite completa (comando de la CI): 2212 en verde.
