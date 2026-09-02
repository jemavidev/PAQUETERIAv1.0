# 289 — Agregar WhatsApp (Meta) y Llamadas (PBX) a `/administracion/proveedores`

**Pedido original (cliente):** "necesito que agregues los formularios de
whatsapp y de las posibles llamadas, ten presente que esta sera la gestion
de los provedores de notificaciones o comunicaciones. [...] Whatsapp
(Notificaciones en general basado en las plantillas existentes, este
modulo no se ha desarrollado y no se hara por ahora, solo tener una
plantilla base de lo que podra el configurar los datos de meta
'informacion generica') por ultimo Llamadas (estas permitiran de alguna
forma automatizar llamadas o mensajes a los clientes, para esta solo deja
planteado lo que sera una posible pbx en issabel, solo deja planteado los
formularios, esta informacion debe estar deshabilitada)." — seguido de
"Los nombre dejalos con META y PXB" (prefijo de las variables de entorno).

**Status:** implementado -- pendiente confirmar en vivo en test.papyrus.com.co

## Alcance acordado

Extiende la pantalla ya existente de `.scratch/administracion-proveedores`
(tickets 01-06, ya verificados en vivo) con dos canales nuevos del catálogo
(`app/domain/proveedores_catalogo.py`). El `CanalNotificacion` enum ya tiene
`WHATSAPP`/`LLAMADA` (se usan en las plantillas de notificación); lo que
falta es agregarlos al catálogo de PROVEEDORES.

- **WhatsApp → proveedor `META`**: funcional, igual que SMS/SMTP —
  habilitado/orden en BD, credenciales vía el mecanismo SSH real (issue 04),
  auditoría. Sin `Sender` real detrás todavía (no se construye ni se
  construirá por ahora) — el catálogo solo deja el terreno listo. Campos:
  `META_APP_ID`, `META_PHONE_NUMBER_ID`, `META_ACCESS_TOKEN`,
  `META_BUSINESS_ACCOUNT_ID`, `META_WEBHOOK_VERIFY_TOKEN` (datos genéricos
  de una app de WhatsApp Business Cloud API de Meta).
- **Llamadas → proveedor `PXB`**: visible pero **deshabilitado** — toggle y
  campos con `disabled` (tanto en HTML como validado del lado servidor, para
  que un POST armado a mano tampoco lo cuele). Campos planteados para una
  futura integración con una PBX Issabel: `PXB_HOST`, `PXB_PUERTO`,
  `PXB_USUARIO`, `PXB_SECRETO`, `PXB_EXTENSION_ORIGEN`.

Mecanismo de "deshabilitado": nuevo campo `disponible: bool = True` en
`ProveedorInfo` (catálogo) — `False` en `PXB`. La pantalla y la ruta POST lo
respetan.

## Implementación

`app/domain/proveedores_catalogo.py`: `CATALOGO["WHATSAPP"]` (proveedor
`META`, `disponible=True`) y `CATALOGO["LLAMADA"]` (proveedor `PXB`,
`disponible=False`) con los campos acordados. Nuevo campo `disponible: bool
= True` en `ProveedorInfo`. `AWS_ACCESS_KEY_ID` pasó a `secreto=False`
(issue 291, confirmado por el cliente). El diseño final de "deshabilitado"
para `PXB` (visible con `disabled` en HTML, no oculto) quedó resuelto junto
con issue 290 -- ver ese archivo para el detalle de las iteraciones en vivo.

## Verificación

Suite completa: 1316 passed. `tests/web/test_admin_proveedores.py`: 22
passed (incluye WhatsApp editable, Llamadas bloqueada, POST defensivo).
Verificado manualmente en el navegador contra `localhost:8010`. Pendiente
confirmar en vivo contra `test.papyrus.com.co`.
