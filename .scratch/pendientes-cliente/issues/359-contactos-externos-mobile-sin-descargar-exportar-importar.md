# 359 — `/administracion/contactos-externos` mobile: no se pueden usar Descargar / Exportar / Importar

**Pedido original (Jesús):** "Necesito que en la vista de
/administracion/contactos-externos, para la version mobil no sea posible usar
el sistema de plantillas 'Descargar, Exportar, Importar'."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Decisiones

- Mobile = `< md` (768px), el mismo corte que usa la paginación de esta vista.
- La fila de los 3 botones queda `hidden md:flex`.
- El formulario de import (que el botón "Importar" despliega) se envuelve en
  `hidden md:block`: aunque estuviera abierto y la pantalla se achicara
  (rotar una tablet), en mobile nunca se ve.
- Es solo visibilidad de UI: las rutas `/plantilla`, `/exportar` e
  `/importar` siguen iguales para admin (no hay forma confiable de distinguir
  "mobile" en el servidor).

## Verificación

- `test_botones_de_plantilla_y_formulario_de_import_se_ocultan_en_mobile`
  (fila `hidden md:flex`, formulario dentro de `hidden md:block`).
- Solo se comprobó el markup; pendiente verlo en un viewport mobile real.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar visualmente". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
