# 220 — `/mis-datos`: modal de "Convertir en principal" igual al de `/residentes`

**Pedido original (cliente):** "Convierte el modal para convertir a un
residente en principal, necesito que sea igual al que se usa en
/residentes."

**Status:** implementado

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
