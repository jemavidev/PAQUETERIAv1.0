# 220 — `/mis-datos`: modal de "Convertir en principal" igual al de `/residentes`

**Pedido original (cliente):** "Convierte el modal para convertir a un
residente en principal, necesito que sea igual al que se usa en
/residentes."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Implementación

`verify.html`: el botón "⭐ Principal" reemplaza su `confirm()` nativo por
`modal_confirmacion` (`components/_modales.html`), mismo componente y mismo
texto que ya usa `customers_manage/detail.html` para esta misma acción
("Se degrada automáticamente a quien es principal ahora."). Se agregó el
toggle genérico `data-open`/`data-close` (delegado sobre `document`, mismo
contrato que el resto del sistema) directo en el `<script>` de la página --
sin llamar a `recursos_recibir()` (el macro que ya trae ese mismo toggle en
`/residentes`), que arrastraría JS de escaneo de guía y picker de
Torre/Apartamento que esta vista de cliente no usa.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
