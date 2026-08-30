# 237 — `/mis-datos`: "Mudarse de este apartamento" pasa a modal

**Pedido original (cliente):** "necesito que para estas vistas de
residentes TODAS las interacciones como por ejemplo '¿Mudarse de este
apartamento? Tus datos quedarán solo de consulta.' no sean manejadas por
el navegador... identifícalas y dime cuáles son para solicitarte cuáles
corregir." Tras revisar `/mis-datos` y `/residentes` completas, el único
`confirm()` nativo que quedaba en toda la sección era este -- el resto ya
se había convertido a modal en trabajo anterior (issues 224/229,
"conversación 2026-08-20"). Cliente confirmó: "Sí, conviértelo".

**Status:** implementado

## Alcance

Vista de un Ocupante NO principal (`customer/verify.html`, roster de solo
lectura, botón de autodescarte "Mudarse de este apartamento"). Mismo
componente `modal_confirmacion` que ya usa el resto de la vista.
