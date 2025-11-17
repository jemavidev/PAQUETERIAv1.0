## Inventario global de canales (EMAIL / WHATSAPP / SMS)

Actualizado: **17-Nov-2025**

### Convenciones rápidas

| Etiqueta | Significado |
| --- | --- |
| `Activo (manual)` | La vista ofrece un CTA (botón, formulario, enlace) que el usuario debe accionar. |
| `Activo (automático)` | El canal se dispara desde backend luego de una acción (guardar anuncio, cambiar estado, etc.). |
| `Display / Captura / Informativo` | El canal solo se muestra, se recolecta, o se describe; no hay CTA directo. |
| `Inactivo` | No existe referencia al canal en la vista. |

---

### Vistas públicas

| Vista | Ruta(s) | Email | WhatsApp | SMS | Notas |
| --- | --- | --- | --- | --- | --- |
| Anunciar paquete (full) | `/announce` | Inactivo | Inactivo | **Activo (automático)** – al guardar el formulario se invoca `SMSService.send_sms_by_event`. | El modal informa al usuario que recibirá un SMS de confirmación. |
| Anunciar paquete (simple) | `/announce-simple` | Inactivo | Inactivo | Inactivo | Pantalla de smoke test sin lógica de canales. |
| Buscar paquetes | `/search` | **Activo (manual)** – formulario “¿Tienes alguna pregunta?” dispara `POST /api/messages/customer-inquiry`. | **Activo (manual)** – los resultados usan `createWhatsAppLinkHTML` para generar `wa.me`. | Informativo – la UI solo explica que backend manda SMS cuando cambia el estado. | También valida/captura emails existentes por tracking. |
| Mensajes públicos | `/messages` | Display – se muestra el correo del remitente para responder fuera del sistema. | **Activo (manual)** – `createPhoneLinksHTML` ofrece WhatsApp + llamada. | Inactivo en UI (las notificaciones SMS se manejan en backend). | El modal de detalle es el punto de contacto. |
| Autenticación (login/register/forgot/reset) | `/auth/login`, `/auth/register`, `/auth/forgot-password`, `/auth/reset-password` | `register`: captura email. `forgot-password`: **activo (manual)** envía enlace de recuperación. `reset-password`: inactivo. | Inactivo | Inactivo | Cada vista solo cubre su flujo de auth. |
| Centro de ayuda | `/help` | **Activo (manual)** – enlace `mailto:soporte@...`. | Inactivo (solo `tel:`). | Informativo – explica que el sistema envía SMS al anunciar. | Incluye botón de llamada directa. |
| Políticas / Contacto | `/policies` | **Activo (manual)** – correo corporativo. | **Activo (manual)** – muestra WhatsApp oficial. | Informativo – detalla los usos de SMS. | También enumera teléfono y horarios. |
| Cookies | `/cookies` | Inactivo | Inactivo | Inactivo | Página legal. |
| Páginas demo/test (`demo_*`, `test_*`, `debug_*`) | varias | Inactivos | Inactivos | Inactivos | Solo QA/documentación visual. |

---

### Vistas protegidas (requieren sesión)

| Vista | Ruta(s) | Email | WhatsApp | SMS | Notas |
| --- | --- | --- | --- | --- | --- |
| Dashboard admin | `/admin` | Inactivo | Inactivo | Inactivo | Navegación principal. |
| Gestión de usuarios | `/admin/users` | **Captura** – formularios de alta/edición solicitan email. | Inactivo | Inactivo | No hay `mailto`. |
| Configuración personal | `/settings` | **Activo (manual)** – switch “Notificaciones por Email”. | Inactivo | **Activo (manual)** – switch “Notificaciones SMS”. | Solo persiste preferencias; no envía mensajes. |
| Perfil (ver/editar) | `/profile`, `/profile/edit`, `/profile/change-password` | `edit`: **captura** email. Otras vistas: inactivas. | Inactivo | Inactivo | Cambiar contraseña solo maneja campos de seguridad. |
| Gestión de paquetes (vista principal) | `/packages` | **Activo (manual)** – bloque “Notificación por Email” → `POST /api/packages/{id}/send-email?event_type=...`. | **Activo (manual)** – detalles muestran enlaces `wa.me`. | **Activo (automático)** – `PackageStateService` envía SMS al recibir/entregar/cancelar. | Modal principal concentra los tres canales. |
| Lista compacta de paquetes | `/packages/list` | Inactivo | **Activo (manual)** – `data-phone` convertido por `base.html`. | Inactivo | Útil para filtros rápidos. |
| Detalle de paquete (admin) | `/packages/{id}` | Inactivo | Inactivo (solo texto simple). | **Activo (automático)** – cambiar estado llama a `PackageStateService`. | Usa botones “Recibir / Entregar / Cancelar”. |
| Recepción manual | `/receive` | **Activo (manual)** – CTA “Enviar Email de Notificación”. | Inactivo | **Activo (automático)** – registrar recepción dispara SMS. | Mostrar email solo si el cliente lo tiene. |
| Detalle de anuncio | `/announcements/{id}`, `/announcements/guide/{guide}` | Inactivo | **Activo (manual)** – `data-phone` con `createPhoneLinksHTML`. | **Activo (automático)** – procesar el anuncio crea paquetes y envía SMS según estado. | Vista puente entre anuncio y paquete real. |
| Gestión de clientes (lista) | `/customers/manage` | **Activo (manual)** – `mailto` por fila + formularios de edición. | **Activo (manual)** – icono `https://wa.me/...` por cliente. | Inactivo | Tabla administrativa completa. |
| Crear/editar cliente | `/customers/create`, `/customers/edit/{id}` | **Captura / edición** de email. | Inactivo | Inactivo | Formularios CRUD. |
| Gestor avanzado de clientes | `/customers/customers` | **Captura** (formularios embebidos). | Inactivo | Inactivo | SPA administrativa (Alpine/HTMX). |
| Gestión de archivos | `/files` | Inactivo | Inactivo | Inactivo | Solo operaciones de storage. |
| Gestión de tarifas | `/rates` | Inactivo | Inactivo | Inactivo | Consola de precios. |
| Gestión de reportes | `/reports` | Inactivo | Inactivo | Informativo – muestra métricas de SMS y link a `/sms`. | No envía mensajes por sí misma. |
| Consola de SMS | `/sms` | Inactivo | Inactivo | **Activo (manual)** – formularios “Enviar SMS” y “Probar SMS” contra los endpoints de notificaciones. | Pantalla de laboratorio para administradores. |
| Vista `update/update.html` | `/update` | Inactivo | Inactivo | Inactivo | Placeholder textual. |
| `deliver/deliver.html` | `/deliver` | Inactivo | Inactivo | Inactivo | Placeholder vacía. |

---

### Vistas híbridas / adicionales

| Vista | Ruta(s) | Email | WhatsApp | SMS | Notas |
| --- | --- | --- | --- | --- | --- |
| Landing autoservicio de anuncios | `/customers/announce` | Inactivo | Inactivo | **Activo (automático)** – la página informa que se envía SMS tras el anuncio. | Versión experimental para clientes finales. |
| Dashboard operativos | `/dashboard` | Inactivo | **Activo (manual)** – cards usan `data-phone` → `createPhoneLinksHTML`. | Inactivo | Permite saltar al detalle del anuncio. |
| Detalle enriquecido (SPA) | `/packages/detail` | Inactivo | **Activo (manual)** – `createWhatsAppLinkHTML` cuando se cargan datos. | Inactivo | Consumido por dashboard público. |
| Gestión visual de anuncios | `/packages/package_management` | Inactivo | **Activo (manual)** – `createWhatsAppLinkHTML` en tarjetas/modales. | Inactivo | UI adicional para operadores. |
| Formularios “nuevo” / “actualizar” paquete | `/packages/new`, `/packages/update` | Inactivos | Inactivos | Inactivos | Solo CRUD. |
| General: Guía de estándares | `/general/guia-estandares` | Inactivo | Inactivo | Inactivo | Catálogo de componentes. |

---

### Plantillas de email (salientes)

| Plantilla | Email | WhatsApp | SMS | Notas |
| --- | --- | --- | --- | --- |
| `templates/emails/*.html` (announcement, delivery, status change, cancel, payment reminder, generic, password reset, base) | **Activo (contenido saliente)** – usan `{{ company_email }}` y textos de notificación. | Inactivo | Inactivo | Se renderizan a través de `EmailService` cuando el backend lo requiere. |

---

### Componentes y layout

| Recurso | Email | WhatsApp | SMS | Notas |
| --- | --- | --- | --- | --- |
| `base/base.html` | Footer con `mailto` y `tel:+57...`. | **Activo (manual)** – footer + utilidades `createWhatsAppLink*` y `createPhoneLinksHTML` que convierten cualquier elemento con `data-phone`. | Inactivo | Cualquier vista que incluya `data-phone` hereda automáticamente los iconos de contacto. |
| `templates/components/*` (navbar, alertas, validadores, etc.) | Inactivo | Inactivo | Inactivo | Solo piezas de UI reutilizables. |

---

## Formatos recomendados para mantener la documentación

1. **Tabla maestra (Markdown/CSV)** – columnas `Vista`, `Ruta`, `Canal`, `Estado`, `Modo`, `Descripción`, `Fuente`. Permite ordenar/filtrar fácilmente por canal.
2. **Matriz por canal** – secciones “Email”, “WhatsApp” y “SMS” con las vistas donde están activos; útil para auditorías enfocadas en un solo canal.
3. **Catálogo JSON/YAML** – estructura tipo:
   ```yaml
   /packages:
     email:
       active: true
       mode: manual
       trigger: "Botón Enviar Email"
     whatsapp:
       active: true
       mode: manual
       trigger: "Link en detalle del cliente"
     sms:
       active: true
       mode: automatic
       trigger: "Cambio de estado en PackageStateService"
   ```
   Ideal para scripts de verificación o documentación automatizada.
4. **Checklist de cumplimiento** – lista de vistas con casillas ☑️/⬜ para “CTA Email”, “CTA WhatsApp”, “Trigger SMS documentado”. Funciona como backlog para unificar experiencias.
5. **Mapa visual (Miro / Draw.io)** – diagrama por vista con etiquetas de color (verde = activo, rojo = inactivo) y flechas indicando si el disparo lo realiza el usuario o el backend.
