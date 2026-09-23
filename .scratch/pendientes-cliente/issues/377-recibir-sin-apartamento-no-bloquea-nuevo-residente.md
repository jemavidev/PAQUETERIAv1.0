# 377 — Recibir: no tener apartamento nunca bloquea la recepción ("Nuevo residente" sin apartamento)

**Pedido original (Jesús):** apareció "Este paquete no tiene apartamento resuelto en su snapshot." al recibir — "el
hecho que no tenga un apartamento resuelto no debería ser impedimento para recibir un paquete ya que en ocasiones los
paquetes no están asociados a un apartamento". Aprobó las 3 correcciones propuestas: "recuerda el no tener un
apartamento no debería bloquear para recibir".

**Status:** implementado, pendiente confirmar en vivo

## Diagnóstico

Recibir sin apartamento YA funcionaba si no se tocaba la sección de residente. El bloqueo ocurría solo al marcar
"Nuevo residente" (que el modal ofrece aunque el paquete no tenga unidad) sin elegir Torre/Apartamento en el selector:
`_resolver_desde_candidato` (`routes/packages.py`) necesita una unidad donde registrar al Ocupante, y `receive_action`
cancelaba TODA la recepción con ese mensaje técnico, descartando guía, tipo, condición y fotos. Recibir mezclaba la
recepción física (no necesita unidad) con el registro del residente (sí la necesita).

## Decisiones

1. **Recibir nunca se bloquea por falta de apartamento.** Si se marcó "Nuevo residente" (o se tecleó un nombre) y el
   paquete sigue sin unidad tras el selector del mismo envío, el paquete se recibe igual y solo se omite el registro
   como Ocupante.
2. **No se pierde lo tecleado.** El nombre (y el teléfono, si el contacto es un teléfono válido) pasan a ser el
   destinatario del paquete (`corregir_destinatario`). Un usuario de WhatsApp o un contacto inválido no bloquean: se
   guarda solo el nombre. Sin nombre, nada que corregir. Tras recibir, aviso fijo: el paquete se recibió pero el nuevo
   residente no se registró por no tener apartamento; se puede asignar después.
3. **El modal lo evita.** Mientras el paquete no tenga unidad y no se haya elegido Torre/Apartamento en el selector,
   la tarjeta "Nuevo residente" queda deshabilitada con la nota "Elige primero el apartamento"; al elegirlo se
   habilita.

Con apartamento, todo sigue igual (incluidas sus validaciones: falta de nombre, contacto inválido, mudar de otra
unidad, bloqueo del issue 189).

## Verificación

- `tests/web/test_recibir_sin_apartamento.py` (8, 7 fallaban antes del cambio): "Nuevo residente" sin unidad recibe
  igual y guarda nombre/teléfono como destinatario (guía conservada, ningún Ocupante creado); aviso sin "snapshot";
  sin nombre no toca el destinatario; WhatsApp/contacto inválido guarda solo el nombre; nombre sin tarjeta tampoco
  bloquea; desde /consultar también recibe; el modal renderiza la tarjeta deshabilitada con su nota.
- `tests/browser/test_recibir_sin_apartamento.py`: la tarjeta se habilita al elegir Torre/Apartamento y se
  deshabilita (desmarcada, sección cerrada) al cambiar el apartamento.
- Regresión: `test_packages`, `test_search`, `test_announce_new`, `test_layout` (426) y seam `browser` (76) en verde.
- Tailwind reconstruido (clases `peer-disabled:*`, `has-[:disabled]:*`) y `?v=101` en `base.html`.
