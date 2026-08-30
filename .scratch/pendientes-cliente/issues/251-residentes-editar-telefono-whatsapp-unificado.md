# 251 — `/residentes/{id}` tab Residentes: modal "Editar" unificado (Teléfono/WhatsApp)

**Pedido original (cliente):** tras comparar el tab "Residentes" de
`/mis-datos` con el de `/residentes` (a pedido del cliente, "dime que
encuentras y que no aplicaría") y confirmar el hallazgo, el cliente pidió
explícitamente: "listo tienes razón cambia a la forma de editar."

**Status:** implementado

## Alcance

`customers_manage/detail.html` (tab Residentes) -- reemplaza los botones
sueltos por fila (✕ Teléfono, ✕ WhatsApp, `<details>` + Teléfono/+
WhatsApp, formularios "Actualizar" separados) por el mismo modal "Editar"
unificado que ya usa `/mis-datos` (issues 227-229): un solo botón
Guardar, Teléfono y WhatsApp en el mismo `<form>`, con "Quitar
teléfono"/"Quitar WhatsApp" debajo de un borde (mismos endpoints
`desvincular-telefono`/`desvincular-whatsapp` que ya existían).

**Sin Nombre/Email** en este modal, a propósito (confirmado con el
cliente en la comparación previa) -- esos ya se editan en la ficha PROPIA
de ese residente (tab Datos, alcanzable por el link de su nombre en esta
misma fila, issue 224). Tampoco se agrega modal de Notificaciones acá,
mismo motivo -- ya existe como tab completa en esa ficha propia.

Ruta nueva `POST /residentes/{persona_id}/ocupantes/{ocupante_id}/editar`
-- mismo patrón que `customer_ocupante_editar` (agrega o edita cada canal
según si la Persona ya lo tenía, re-consultando la Persona vigente entre
Teléfono y WhatsApp por si `editar_telefono_ocupante` re-ligó
`persona_id`). Las rutas viejas (`/telefono`, `/whatsapp`) se quedan
intactas, mismo criterio que ya se usó del lado cliente cuando se hizo
este mismo cambio.

## Seguimiento: Nombre/Email + Notificaciones

El cliente probó el resultado y pidió más: "incluye Nombre/Email (editar)
y Notificaciones (Notificaciones), pero al hacer click en 'Notificaciones'
redirígenos al tab de notificaciones de ese usuario." Implementado:

- **Nombre/Email**: agregados al modal "Editar" (antes excluidos a
  propósito). La ruta `/editar` ahora también acepta `nombre`/`email` y
  llama `update_datos_personales` -- mismo patrón exacto que
  `customer_ocupante_editar`. `_ocupantes_de` gana el atributo transitorio
  `o.email` (igual que ya tenía `o.telefono`/`o.whatsapp_usuario`).
- **Notificaciones**: NO es un modal (a diferencia de Editar) -- es un
  link `<a>` (mismo estilo `chip_accion`) a `/residentes/{o.persona_id}
  ?tab=notif`, la tab Notificaciones YA existente en la ficha propia de
  ese residente (mismo mecanismo `?tab=` que el link del nombre, issue
  100/172/224). Evita duplicar la matriz Canal×Evento en dos lugares.

2 tests nuevos (Nombre/Email vía la ruta, presencia del link
`?tab=notif`) -- 136 tests en verde. Verificado en vivo por curl: el modal
trae los 4 campos, los 3 links de Notificaciones apuntan a la persona
correcta, y un submit real de Email vía la ruta nueva se guardó sin tocar
el Teléfono.
