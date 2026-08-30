# 227 — `/mis-datos` tab Residentes: unificar edición (Nombre/Email/Teléfono/WhatsApp) en un solo panel

**Pedido original (cliente):** "se ve bastante bien la lógica, de qué forma
puedes unificar esto para los datos existentes y lo nuevo que acabas de
agregar, esto con el fin que los botones existentes realicen estos cambios
y se visualice de mejor forma y más homogeneidad." (seguimiento de
[[226-mis-datos-residentes-editar-nombre-email-notificaciones]]).

**Status:** implementado

## Implementación

Antes: hasta 5 piezas sueltas por residente (chips "+ Teléfono"/"+
WhatsApp", los `<form>` "Actualizar" de teléfono/WhatsApp SIEMPRE visibles
debajo de la tarjeta -- no colapsados como el resto --, y el chip "✏️
Editar" con solo Nombre/Email del issue 226). Ahora: un solo `<details>`
"✏️ Editar" agrupa Nombre+Email, Teléfono y WhatsApp -- cada campo apunta
al MISMO endpoint de siempre (`/telefono`, `/whatsapp`, `/datos`), que ya
decidía agregar vs. editar de forma transparente (issue 213/217) -- así
que un solo input+botón "Guardar" sirve para los dos casos, sin
duplicar el campo en dos piezas de UI distintas. "Quitar teléfono"/"Quitar
WhatsApp" se mudaron de chip aparte a un enlace chico junto a su propio
campo, dentro del mismo panel.

Chips visibles por residente: de hasta 7 (⭐ Promover, ✕ Teléfono, ✕
WhatsApp, + Teléfono, + WhatsApp, ✏️ Editar, 🔔 Notificaciones) a 3 (⭐
Promover, ✏️ Editar, 🔔 Notificaciones).

Sin cambios de backend -- las 3 rutas (`/telefono`, `/whatsapp`, `/datos`)
son las mismas de los issues 213/217/226, solo se reorganizó la plantilla.
