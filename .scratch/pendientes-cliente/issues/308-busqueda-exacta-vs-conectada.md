# 308 — Búsqueda "exacta" vs "conectada" (toggle) por Nombre/Teléfono/Email/WhatsApp

**Pedido original (cliente):** buscar "jesus" trae paquetes de OTRAS personas (Daniela, Angélica)
solo porque Jesús las anunció -- pide un botón/ícono que alterne entre mostrar SOLO las
coincidencias exactas (destinatario real) y, al presionarlo, SOLO las conexiones (paquetes donde
el término buscado matchea al Anunciante, no al destinatario). Aplica a los 4 campos de texto:
Nombre, Teléfono, Email, Usuario de WhatsApp.

**Status:** implementado -- pendiente verificar visualmente en vivo (extensión de Chrome no
disponible en esta sesión). Verificado end-to-end contra el servidor real (`localhost:8010`) con
los datos reales del caso "JESUS VILLALOBOS": `q=jesus` sin `conectados` -> 6; con `conectados=true`
-> 2 (MASE, KTN4). Igual para email. 225 + 158 tests relacionados en verde
(`test_packages.py`/`test_customers_manage.py`/`test_layout.py`).

## Validado contra datos reales antes de implementar (residente real "JESUS VILLALOBOS")

| Campo | Exacto | Conectado |
|---|---|---|
| Nombre ("jesus") | 6 | 2 (KTN4, MASE) |
| Email (jveyes@gmail.com) | 6 | 2 (KTN4, MASE) |
| Teléfono (+573002596319) | 7 (incluye 9KN3, préstamo de teléfono de Daniela) | 2 (KTN4, MASE) |

Regla validada: "exacto" = coincide con un campo PROPIO del Paquete (`recipient_name`/
`recipient_phone`) o, para Email/WhatsApp (que no tienen versión propia del destinatario en el
modelo -- ADR-0007), el Anunciante coincidiendo consigo mismo (`Persona.nombre` == `recipient_name`,
"para mí mismo"). "Conectado" = coincide SOLO vía el Anunciante (`Persona.nombre/email/
whatsapp_usuario`, `announced_by_phone`) Y ese Anunciante NO es el propio destinatario. El caso
9KN3 (teléfono prestado, `recipient_phone` = teléfono de Jesús) queda del lado "exacto" a
propósito -- es un dato propio del paquete, confirmado con el cliente que NO debía romperse.

## Diseño de interacción confirmado con el cliente

Ícono/botón junto a la barra de búsqueda, mismo lenguaje visual que los íconos de Estado
existentes -- alterna un parámetro (`conectados=1`) que cambia el SET de condiciones SQL completo
(nunca mezcla los dos sets). Aplica a los 4 campos de texto (Nombre/Teléfono/Email/WhatsApp) con
la misma regla; NO aplica a código de acceso/guía/Torre/Apto (no tiene sentido "conectado" ahí).
