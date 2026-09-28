# Análisis de enlaces de PaqueteX v2 (2026-09-27)

Revisión automática + manual de TODOS los enlaces que genera la app (`CODE/src/app/web`): `href`, `action` de
formularios, destinos pasados a macros (`enlace_menu`, `formulario_flujo`, `modal_confirmacion`, paginación…), URLs
armadas en JavaScript (`fetch`, `location.assign`), redirecciones del servidor (`RedirectResponse`) y enlaces que
salen de la app (WhatsApp, `tel:`, SMS, correos). Cada destino se cruzó contra las 143 rutas reales de la app
(introspección de `app.routes`), con su método HTTP y sus parámetros de consulta.

## Resultado

- **379 enlaces** en 89 archivos. **Ninguno apunta a una ruta inexistente** y ninguno usa un método que la ruta no
  acepte (los 8 formularios que parecían GET son `formulario_flujo`/`modal_confirmacion`, que envían POST por defecto).
- Todos los archivos estáticos enlazados (`/static/...`) existen.

## Hallazgos

1. **`/docs`, `/redoc` y `/openapi.json` están públicos** (200 sin sesión en `test.papyrus.com.co`): publican el mapa
   completo de las 143 rutas y sus parámetros. FastAPI los crea por defecto (`FastAPI(title=...)` en `web/app.py:104`
   sin `docs_url=None`). Recomendado: apagarlos fuera de desarrollo.
2. **Mensajes de confirmación que nunca se muestran** -- la redirección agrega un parámetro que ninguna vista lee:
   - `/otp?telefono_actualizado=1` (`routes/customer_verify.py:431`): el residente cambia su teléfono, se le cierra la
     sesión y cae en "Verificar mi teléfono" sin ninguna explicación.
   - `/otp?cuenta_eliminada=1` (`routes/customer_verify.py:511`): tras eliminar su cuenta, la misma pantalla de
     ingreso sin confirmación.
   - `/residentes?eliminado=1` (`routes/customers_manage.py:1740`): el staff elimina un residente y la lista no dice
     nada. (Los `?eliminado` de motivos sí se muestran.)
   Verificado: `/otp` devuelve exactamente la misma página con y sin esos parámetros.
3. **`PUBLIC_BASE_URL` fijo en `test.papyrus.com.co`** (`docker-compose.yml` del repo de despliegue): es la base de
   los enlaces de SMS/WhatsApp/correo (`/consultar?q=<código>`, `/ayuda`, restablecer contraseña). En el paso a
   producción hay que cambiarlo o los residentes recibirán enlaces a test. El mensaje de WhatsApp de Acciones usa
   `public_base_url_relaxed() or ''`: sin la variable, el enlace sale relativo e inservible fuera de la app.
4. **Rutas sin ningún enlace que lleve a ellas** (no es un error, para saberlo):
   - `/administracion/estadisticas-cobro` y `/otp/perfil`: URLs viejas que solo redirigen (a `/administracion/dashboard`
     y `/mis-datos`). `auth/customer_me.html` quedó sin uso.
   - `/` (redirige a `/anunciar`) y `/health` (monitoreo).
   - `/paquetes/{id}/timeline` y `/paquetes/promover-candidatos`: se llaman por JS, no son páginas.

## Enlaces que salen de la app

| Qué | Destino | Dónde se arma |
|---|---|---|
| WhatsApp (móvil) | `https://wa.me/<número o usuario>?text=…` | `domain/persona_service.py:460`, `web/routes/packages.py:268` |
| WhatsApp (escritorio) | `https://web.whatsapp.com/send?phone=<número>&text=…` | `domain/persona_service.py:489`, `web/routes/packages.py:268` |
| Llamar | `tel:<teléfono>` | `domain/persona_service.py:497` |
| SMS / WhatsApp automáticos | `{link}` = `PUBLIC_BASE_URL/consultar?q=<código>` | `domain/notificacion_service.py:155` |
| Correo (pie) | `PUBLIC_BASE_URL/consultar`, `PUBLIC_BASE_URL/ayuda` | `domain/plantilla_email_html.py:32` |
| Correo de contraseña | `PUBLIC_BASE_URL/staff/restablecer-password?token=…` | `web/routes/password_reset.py:34` |
| Footer WhatsApp soporte | `wa.me/<WHATSAPP_SOPORTE_NUMERO>` (oculto si no está configurado) | `web/config.py` |

## Enlaces armados en JavaScript

| Destino | Dónde |
|---|---|
| `GET /announce/identificar`, `/identificar-sugerencia`, `/identificar-contacto`, `/identificar-ocupante` | `announce_new/form.html` |
| `GET <action de la barra>?q=…` (búsqueda en vivo de /paquetes y /residentes) | `components/_busqueda_filtros.html:406` |
| `GET /paquetes/{id}/timeline` (historial del modal Ver) | `components/_recibir_paquete.html:474` |
| `GET /paquetes/guia-repetida?guia=…` | `components/_recibir_paquete.html:900` |
| `GET /paquetes/{id}/nuevo-residente/identificar`, `/residentes/{id}/ocupantes/identificar` | `_recibir_paquete.html`, `packages/_resultados.html`, `customers_manage/detail.html` |
| `POST /paquetes/{id}/fotos` (cola de fotos) | `base.html:778`, `components/_carga_fotos.html:189` |
| `POST /actividad`, `POST /bloquear`, `GET/POST /bloqueo` (PIN de operador) | `components/_capa_bloqueo.html`, `auth/bloqueo.html` |

## Mapa por página: desde dónde se llega a cada ruta

| Ruta | Métodos | Desde dónde se llega |
|---|---|---|
| `/` | GET | — |
| `/health` | GET | — |
| `/anunciar` | GET | announce/confirmar_multiple.html, announce/form.html, ayuda/form.html, base.html, como_funciona/form.html, components/_formularios.html, routes/announce.py, routes/auth.py, web/app.py, web/templates/announce/form.html, web/templates/components/_estado_vacio.html, web/templates/components/_formularios.html |
| `/anunciar/confirmacion` | GET | routes/announce.py |
| `/anunciar` | POST | announce/confirmar_multiple.html, announce/form.html, ayuda/form.html, base.html, como_funciona/form.html, components/_formularios.html, routes/announce.py, routes/auth.py, web/app.py, web/templates/announce/form.html, web/templates/components/_estado_vacio.html, web/templates/components/_formularios.html |
| `/ingresar` | GET | auth/bloqueo.html, auth/entrar.html, auth/login.html, auth/olvide_password_enviado.html, components/_capa_bloqueo.html, routes/auth.py, routes/password_reset.py, web/templates/auth/login.html |
| `/ingresar` | POST | auth/bloqueo.html, auth/entrar.html, auth/login.html, auth/olvide_password_enviado.html, components/_capa_bloqueo.html, routes/auth.py, routes/password_reset.py, web/templates/auth/login.html |
| `/mi-pin` | GET | auth/pin.html, base.html, routes/auth.py, web/templates/auth/pin.html |
| `/mi-pin` | POST | auth/pin.html, base.html, routes/auth.py, web/templates/auth/pin.html |
| `/bloqueo` | GET | base.html, components/_capa_bloqueo.html, routes/auth.py |
| `/bloqueo` | POST | base.html, components/_capa_bloqueo.html, routes/auth.py |
| `/bloquear` | POST | base.html |
| `/actividad` | POST | — |
| `/mi-pin/cerrar-todos` | POST | auth/pin.html |
| `/salir-dispositivo` | POST | base.html |
| `/salir` | POST | — |
| `/salir-todo` | POST | base.html |
| `/mi-sesion` | GET | auth/me.html, base.html, web/templates/auth/me.html |
| `/mi-sesion/editar` | POST | auth/me.html, web/templates/auth/me.html |
| `/mi-sesion` | POST | auth/me.html, base.html, web/templates/auth/me.html |
| `/administracion/personal` | GET | admin/staff.html, base.html, routes/admin.py |
| `/administracion/personal` | POST | admin/staff.html, base.html, routes/admin.py |
| `/administracion/personal/{usuario_id}/editar` | POST | admin/staff.html |
| `/administracion/personal/{usuario_id}/resetear-password` | POST | admin/staff.html |
| `/administracion/personal/{usuario_id}/cerrar-dispositivos` | POST | admin/staff.html |
| `/administracion/personal/{usuario_id}/activar` | POST | admin/staff.html |
| `/administracion/personal/{usuario_id}/desactivar` | POST | admin/staff.html |
| `/administracion/notificaciones` | GET | admin/notificaciones.html, base.html |
| `/administracion/notificaciones` | POST | admin/notificaciones.html, base.html |
| `/administracion/notificaciones/probar` | POST | admin/notificaciones.html |
| `/administracion/motivos-cancelacion` | GET | admin/motivos_cancelacion.html, base.html, web/templates/admin/motivos_cancelacion.html |
| `/administracion/motivos-cancelacion` | POST | admin/motivos_cancelacion.html, base.html, web/templates/admin/motivos_cancelacion.html |
| `/administracion/motivos-cancelacion/{motivo_id}/editar` | POST | admin/motivos_cancelacion.html |
| `/administracion/motivos-cancelacion/{motivo_id}/eliminar` | POST | web/templates/admin/motivos_cancelacion.html |
| `/administracion/conjunto` | GET | admin/conjunto.html, base.html, web/templates/admin/conjunto.html |
| `/administracion/conjunto` | POST | admin/conjunto.html, base.html, web/templates/admin/conjunto.html |
| `/administracion/conjunto/empresa` | POST | admin/conjunto.html, web/templates/admin/conjunto.html |
| `/administracion/conjunto/seguridad` | POST | admin/conjunto.html, web/templates/admin/conjunto.html |
| `/administracion/tarifas-cobro` | GET | admin/conjunto.html, admin/tarifas_cobro.html, base.html, web/templates/admin/tarifas_cobro.html |
| `/administracion/tarifas-cobro` | POST | admin/conjunto.html, admin/tarifas_cobro.html, base.html, web/templates/admin/tarifas_cobro.html |
| `/administracion/motivos-anulacion-cobro` | GET | admin/motivos_anulacion_cobro.html, base.html, web/templates/admin/motivos_anulacion_cobro.html |
| `/administracion/motivos-anulacion-cobro` | POST | admin/motivos_anulacion_cobro.html, base.html, web/templates/admin/motivos_anulacion_cobro.html |
| `/administracion/motivos-anulacion-cobro/{motivo_id}/eliminar` | POST | web/templates/admin/motivos_anulacion_cobro.html |
| `/administracion/estadisticas-cobro` | GET | — |
| `/administracion/dashboard` | GET | base.html |
| `/administracion/contactos-externos` | GET | base.html |
| `/administracion/contactos-externos/importar` | POST | admin/contactos_externos.html |
| `/administracion/contactos-externos/plantilla` | GET | admin/contactos_externos.html |
| `/administracion/contactos-externos/exportar` | GET | admin/contactos_externos.html |
| `/administracion/migrar-anio` | GET | admin/migrar_anio.html, base.html |
| `/administracion/migrar-anio` | POST | admin/migrar_anio.html, base.html |
| `/administracion/motivos-bloqueo` | GET | admin/motivos_bloqueo.html, base.html, web/templates/admin/motivos_bloqueo.html |
| `/administracion/motivos-bloqueo` | POST | admin/motivos_bloqueo.html, base.html, web/templates/admin/motivos_bloqueo.html |
| `/administracion/motivos-bloqueo/{motivo_id}/eliminar` | POST | web/templates/admin/motivos_bloqueo.html |
| `/administracion/proveedores` | GET | admin/_dashboard_resultados.html, base.html |
| `/administracion/proveedores/{canal}` | POST | admin/proveedores.html |
| `/administracion/respaldos` | GET | base.html, routes/admin_respaldos.py |
| `/administracion/respaldos/ahora` | POST | admin/respaldos.html |
| `/administracion/respaldos/fotos/copiar` | POST | admin/respaldos.html |
| `/administracion/respaldos/fotos/descargar` | GET | admin/respaldos.html |
| `/administracion/respaldos/{nombre}/descargar` | GET | admin/respaldos.html |
| `/administracion/posiciones` | GET | admin/posiciones.html, base.html, web/templates/admin/posiciones.html |
| `/administracion/posiciones` | POST | admin/posiciones.html, base.html, web/templates/admin/posiciones.html |
| `/announce` | GET | announce_new/_identificar_unidad.html, base.html, components/_busqueda_filtros.html, components/_formulario_persona_nueva.html, components/_persona_resuelta.html, web/templates/packages/_resultados.html |
| `/announce/identificar` | GET | announce_new/form.html |
| `/announce/identificar-sugerencia` | GET | announce_new/form.html |
| `/announce/identificar-contacto` | GET | announce_new/form.html |
| `/announce/identificar-ocupante` | GET | announce_new/form.html |
| `/announce` | POST | announce_new/_identificar_unidad.html, base.html, components/_busqueda_filtros.html, components/_formulario_persona_nueva.html, components/_persona_resuelta.html, web/templates/packages/_resultados.html |
| `/ayuda` | GET | base.html, como_funciona/form.html, cookies/form.html, privacy/form.html, terms/form.html |
| `/como-funciona` | GET | announce/confirmacion.html, ayuda/form.html, terms/form.html |
| `/cookies` | GET | ayuda/form.html, privacy/form.html |
| `/otp` | GET | announce/confirmacion.html, components/_confirmacion.html, routes/customer_auth.py, routes/customer_verify.py, search/form.html |
| `/otp/solicitar` | POST | auth/customer_login.html, auth/entrar.html, web/templates/auth/customer_login.html |
| `/otp/verificar` | GET | auth/customer_verify.html, routes/customer_auth.py |
| `/otp/verificar` | POST | auth/customer_verify.html, routes/customer_auth.py |
| `/otp/salir` | POST | auth/customer_me.html |
| `/otp/perfil` | GET | — |
| `/mis-paquetes` | GET | base.html, como_funciona/form.html, terms/form.html |
| `/residentes` | GET | base.html, customers_manage/detail.html, routes/customers_manage.py |
| `/residentes/saldos-contra-entrega` | GET | customers_manage/movimientos_saldo_contra_entrega.html, customers_manage/saldos_contra_entrega.html |
| `/residentes/movimientos-saldo-contra-entrega` | GET | customers_manage/movimientos_saldo_contra_entrega.html, customers_manage/saldos_contra_entrega.html |
| `/residentes/{persona_id}` | GET | customers_manage/_resultados.html, customers_manage/detail.html, customers_manage/movimientos_saldo_contra_entrega.html, customers_manage/saldos_contra_entrega.html, packages/_resultados.html, routes/customers_manage.py |
| `/residentes/{persona_id}` | POST | customers_manage/_resultados.html, customers_manage/detail.html, customers_manage/movimientos_saldo_contra_entrega.html, customers_manage/saldos_contra_entrega.html, packages/_resultados.html, routes/customers_manage.py |
| `/residentes/{persona_id}/notificaciones` | POST | customers_manage/detail.html |
| `/residentes/{persona_id}/apartamento` | POST | customers_manage/_resultados.html, customers_manage/detail.html |
| `/residentes/{persona_id}/ocupantes/identificar` | GET | customers_manage/detail.html |
| `/residentes/{persona_id}/ocupantes` | POST | customers_manage/detail.html |
| `/residentes/{persona_id}/ocupantes/{ocupante_id}/telefono` | POST | — |
| `/residentes/{persona_id}/ocupantes/{ocupante_id}/contacto` | POST | — |
| `/residentes/{persona_id}/ocupantes/{ocupante_id}/whatsapp` | POST | — |
| `/residentes/{persona_id}/ocupantes/{ocupante_id}/editar` | POST | customers_manage/detail.html |
| `/residentes/{persona_id}/ocupantes/{ocupante_id}/baja` | POST | web/templates/customers_manage/detail.html |
| `/residentes/{persona_id}/ocupantes/{ocupante_id}/confirmar` | POST | customers_manage/detail.html |
| `/residentes/{persona_id}/ocupantes/{ocupante_id}/promover` | POST | web/templates/customers_manage/detail.html |
| `/residentes/{persona_id}/eliminar` | POST | web/templates/customers_manage/_resultados.html |
| `/residentes/{persona_id}/baja-administrativa` | POST | web/templates/customers_manage/detail.html |
| `/residentes/{persona_id}/reactivar` | POST | web/templates/customers_manage/detail.html |
| `/residentes/{persona_id}/bloquear` | POST | web/templates/customers_manage/detail.html |
| `/residentes/{persona_id}/autorizar-desbloqueo` | POST | web/templates/customers_manage/detail.html |
| `/residentes/{persona_id}/liberar-bloqueo` | POST | web/templates/customers_manage/detail.html |
| `/residentes/{persona_id}/saldo-contra-entrega/movimiento` | POST | customers_manage/detail.html |
| `/mis-datos` | GET | ayuda/form.html, base.html, como_funciona/form.html, customer/verify.html, privacy/form.html, routes/customer_auth.py, routes/customer_verify.py, routes/entrar.py, terms/form.html |
| `/mis-datos/aceptar-terminos` | GET | customer/aceptar_terminos.html, web/security.py |
| `/mis-datos/aceptar-terminos` | POST | customer/aceptar_terminos.html, web/security.py |
| `/mis-datos` | POST | ayuda/form.html, base.html, como_funciona/form.html, customer/verify.html, privacy/form.html, routes/customer_auth.py, routes/customer_verify.py, routes/entrar.py, terms/form.html |
| `/mis-datos/eliminar-cuenta` | POST | customer/verify.html, web/templates/customer/verify.html |
| `/mis-datos/ocupantes` | POST | customer/verify.html |
| `/mis-datos/ocupantes/{ocupante_id}/contacto` | POST | customer/verify.html |
| `/mis-datos/ocupantes/{ocupante_id}/telefono` | POST | — |
| `/mis-datos/ocupantes/{ocupante_id}/whatsapp` | POST | — |
| `/mis-datos/ocupantes/{ocupante_id}/editar` | POST | customer/verify.html |
| `/mis-datos/ocupantes/{ocupante_id}/notificaciones` | POST | customer/verify.html |
| `/mis-datos/ocupantes/{ocupante_id}/confirmar` | POST | customer/verify.html |
| `/mis-datos/ocupantes/{ocupante_id}/baja` | POST | web/templates/customer/verify.html |
| `/mis-datos/ocupantes/{ocupante_id}/promover` | POST | web/templates/customer/verify.html |
| `/mis-datos/ocupantes/salir` | POST | customer/verify.html, web/templates/customer/verify.html |
| `/entrar` | GET | announce/form.html, ayuda/form.html, base.html, como_funciona/form.html |
| `/paquetes` | GET | base.html, components/_persona_resuelta.html, customers_manage/_resultados.html, routes/auth.py, routes/entrar.py, routes/packages.py |
| `/paquetes/{paquete_id}/timeline` | GET | — |
| `/paquetes/{paquete_id}/fotos` | POST | — |
| `/paquetes/{paquete_id}/recibir` | POST | components/_modales.html, components/_recibir_paquete.html |
| `/paquetes/{paquete_id}/entregar` | POST | packages/_resultados.html, search/form.html |
| `/paquetes/{paquete_id}/cancelar` | POST | components/_botones.html, web/templates/components/_modales.html, web/templates/packages/_resultados.html |
| `/paquetes/{paquete_id}/eliminar` | POST | web/templates/packages/_resultados.html |
| `/paquetes/{paquete_id}/asignar-apartamento` | POST | packages/_resultados.html |
| `/paquetes/{paquete_id}/nuevo-residente/identificar` | GET | components/_recibir_paquete.html, packages/_resultados.html |
| `/paquetes/guia-repetida` | GET | components/_recibir_paquete.html |
| `/paquetes/promover-candidatos` | GET | — |
| `/paquetes/promover-principal` | POST | packages/_resultados.html |
| `/paquetes/{paquete_id}/corregir` | POST | packages/_resultados.html |
| `/staff/olvide-password` | GET | auth/entrar.html, auth/login.html, auth/olvide_password.html, web/templates/auth/olvide_password.html |
| `/staff/olvide-password` | POST | auth/entrar.html, auth/login.html, auth/olvide_password.html, web/templates/auth/olvide_password.html |
| `/staff/restablecer-password` | GET | auth/restablecer_password.html, web/templates/auth/restablecer_password.html |
| `/staff/restablecer-password` | POST | auth/restablecer_password.html, web/templates/auth/restablecer_password.html |
| `/privacidad` | GET | announce/form.html, ayuda/form.html, como_funciona/form.html, cookies/form.html, customer/verify.html, terms/form.html |
| `/consultar` | GET | announce/confirmacion.html, announce_new/form.html, ayuda/form.html, base.html, como_funciona/form.html, components/_confirmacion.html, customer/paquetes.html, customer/verify.html, customers_manage/detail.html, customers_manage/movimientos_saldo_contra_entrega.html, packages/_resultados.html, search/form.html, terms/form.html, web/templates/search/form.html |
| `/terminos` | GET | announce/form.html, ayuda/form.html, como_funciona/form.html, components/_inputs.html, cookies/form.html, customer/aceptar_terminos.html, customer/verify.html |

## Mapa por vista: a dónde lleva cada enlace

### `admin/_dashboard_resultados.html`

| Línea | Tipo | Destino |
|---|---|---|
| 73 | href | `/administracion/proveedores?tab=SMS` |

### `admin/conjunto.html`

| Línea | Tipo | Destino |
|---|---|---|
| 19 | action | `/administracion/conjunto` |
| 33 | action | `/administracion/conjunto/empresa` |
| 43 | action | `/administracion/conjunto/seguridad` |
| 52 | href | `/administracion/tarifas-cobro` |

### `admin/contactos_externos.html`

| Línea | Tipo | Destino |
|---|---|---|
| 54 | href | `/administracion/contactos-externos/plantilla` |
| 55 | href | `/administracion/contactos-externos/exportar` |
| 63 | action | `/administracion/contactos-externos/importar` |

### `admin/migrar_anio.html`

| Línea | Tipo | Destino |
|---|---|---|
| 23 | action | `/administracion/migrar-anio` |

### `admin/motivos_anulacion_cobro.html`

| Línea | Tipo | Destino |
|---|---|---|
| 13 | action | `/administracion/motivos-anulacion-cobro` |
| 28 | action | `/administracion/motivos-anulacion-cobro/` |

### `admin/motivos_bloqueo.html`

| Línea | Tipo | Destino |
|---|---|---|
| 13 | action | `/administracion/motivos-bloqueo` |
| 28 | action | `/administracion/motivos-bloqueo/` |

### `admin/motivos_cancelacion.html`

| Línea | Tipo | Destino |
|---|---|---|
| 20 | action | `/administracion/motivos-cancelacion` |
| 44 | action | `/administracion/motivos-cancelacion/{{ m.id }}/editar` |
| 52 | action | `/administracion/motivos-cancelacion/` |

### `admin/notificaciones.html`

| Línea | Tipo | Destino |
|---|---|---|
| 138 | action | `/administracion/notificaciones` |
| 173 | action | `/administracion/notificaciones/probar` |

### `admin/posiciones.html`

| Línea | Tipo | Destino |
|---|---|---|
| 13 | action | `/administracion/posiciones` |

### `admin/proveedores.html`

| Línea | Tipo | Destino |
|---|---|---|
| 32 | action | `/administracion/proveedores/{{ canal.canal }}` |

### `admin/respaldos.html`

| Línea | Tipo | Destino |
|---|---|---|
| 39 | action | `/administracion/respaldos/ahora` |
| 65 | href | `/administracion/respaldos/{{ r.nombre }}/descargar` |
| 151 | action | `/administracion/respaldos/fotos/copiar` |
| 163 | href | `/administracion/respaldos/fotos/descargar?cuales=nuevas` |
| 164 | href | `/administracion/respaldos/fotos/descargar?cuales=todas` |

### `admin/staff.html`

| Línea | Tipo | Destino |
|---|---|---|
| 70 | action | `/administracion/personal/{{ u.id }}/cerrar-dispositivos` |
| 74 | action | `/administracion/personal/{{ u.id }}/desactivar` |
| 78 | action | `/administracion/personal/{{ u.id }}/activar` |
| 92 | action | `/administracion/personal/{{ u.id }}/editar` |
| 107 | action | `/administracion/personal/{{ u.id }}/resetear-password` |
| 124 | action | `/administracion/personal` |

### `admin/tarifas_cobro.html`

| Línea | Tipo | Destino |
|---|---|---|
| 11 | action | `/administracion/tarifas-cobro` |

### `announce/confirmacion.html`

| Línea | Tipo | Destino |
|---|---|---|
| 10 | src | `/static/branding/papyrus-logo.png` |
| 30 | href | `/consultar` |
| 31 | href | `/otp` |
| 32 | href | `/como-funciona` |

### `announce/confirmar_multiple.html`

| Línea | Tipo | Destino |
|---|---|---|
| 6 | src | `/static/branding/papyrus-logo.png` |
| 21 | action | `/anunciar` |
| 28 | href | `/anunciar` |

### `announce/form.html`

| Línea | Tipo | Destino |
|---|---|---|
| 11 | src | `/static/branding/papyrus-logo.png` |
| 17 | action | `/anunciar` |
| 51 | href | `/entrar` |
| 94 | href | `/terminos` |
| 96 | href | `#aviso-privacidad-detalle` |
| 100 | href | `/privacidad` |

### `announce_new/_identificar_unidad.html`

| Línea | Tipo | Destino |
|---|---|---|
| 114 | action | `/announce` |

### `announce_new/form.html`

| Línea | Tipo | Destino |
|---|---|---|
| 34 | href | `/consultar?q={}` |
| 74 | js | `/announce/identificar?q=` |
| 115 | js | `/announce/identificar-ocupante?` |
| 137 | js | `/announce/identificar-sugerencia?` |
| 193 | js | `/announce/identificar-contacto?` |

### `auth/bloqueo.html`

| Línea | Tipo | Destino |
|---|---|---|
| 13 | href | `/ingresar` |

### `auth/customer_login.html`

| Línea | Tipo | Destino |
|---|---|---|
| 10 | src | `/static/branding/papyrus-logo.png` |
| 14 | action | `/otp/solicitar` |

### `auth/customer_me.html`

| Línea | Tipo | Destino |
|---|---|---|
| 12 | action | `/otp/salir` |

### `auth/customer_verify.html`

| Línea | Tipo | Destino |
|---|---|---|
| 9 | src | `/static/branding/papyrus-logo.png` |
| 16 | action | `/otp/verificar` |

### `auth/entrar.html`

| Línea | Tipo | Destino |
|---|---|---|
| 10 | src | `/static/branding/papyrus-logo.png` |
| 35 | action | `/otp/solicitar` |
| 41 | action | `/ingresar` |
| 49 | href | `/staff/olvide-password` |

### `auth/login.html`

| Línea | Tipo | Destino |
|---|---|---|
| 10 | src | `/static/branding/papyrus-logo.png` |
| 16 | action | `/ingresar` |
| 21 | href | `/staff/olvide-password` |

### `auth/me.html`

| Línea | Tipo | Destino |
|---|---|---|
| 30 | action | `/mi-sesion/editar` |
| 42 | action | `/mi-sesion` |

### `auth/olvide_password.html`

| Línea | Tipo | Destino |
|---|---|---|
| 10 | src | `/static/branding/papyrus-logo.png` |
| 14 | action | `/staff/olvide-password` |

### `auth/olvide_password_enviado.html`

| Línea | Tipo | Destino |
|---|---|---|
| 7 | src | `/static/branding/papyrus-logo.png` |
| 15 | href | `/ingresar` |

### `auth/pin.html`

| Línea | Tipo | Destino |
|---|---|---|
| 17 | action | `/mi-pin` |
| 28 | action | `/mi-pin/cerrar-todos` |

### `auth/restablecer_password.html`

| Línea | Tipo | Destino |
|---|---|---|
| 10 | src | `/static/branding/papyrus-logo.png` |
| 14 | action | `/staff/restablecer-password` |

### `ayuda/form.html`

| Línea | Tipo | Destino |
|---|---|---|
| 14 | src | `/static/branding/papyrus-logo.png` |
| 57 | href | `/como-funciona` |
| 158 | href | `/terminos` |
| 240 | href | `/consultar` |
| 283 | href | `/mis-datos` |
| 365 | href | `/entrar` |
| 439 | href | `/anunciar` |
| 453 | href | `tel:{{ empresa.telefono_contacto }}` |
| 481 | href | `mailto:{{ empresa.email_contacto }}` |
| 498 | href | `/privacidad` |
| 503 | href | `/cookies` |

### `base.html`

| Línea | Tipo | Destino |
|---|---|---|
| 8 | href | `/static/branding/colibri-icono.png?v=1` |
| 16 | href | `/static/css/tailwind.css?v=114` |
| 299 | href | `/bloqueo` |
| 305 | action | `/salir-todo` |
| 322 | menú menu | `/mis-paquetes («Mis paquetes»)` |
| 323 | menú menu | `/mis-datos («Mis datos»)` |
| 324 | menú menu | `/consultar («Consultar»)` |
| 325 | menú menu | `/ayuda («Ayuda»)` |
| 334 | menú menu | `/mi-sesion («Mi perfil»)` |
| 336 | menú menu | `/mi-pin («Mi PIN»)` |
| 339 | menú menu | `/administracion/dashboard («Dashboard»)` |
| 381 | menú menu | `/administracion/conjunto («Conjunto»)` |
| 382 | menú menu | `/administracion/contactos-externos («Contactos externos»)` |
| 383 | menú menu | `/administracion/motivos-bloqueo («Motivos de bloqueo»)` |
| 384 | menú menu | `/administracion/motivos-anulacion-cobro («Motivos de anulación»)` |
| 385 | menú menu | `/administracion/motivos-cancelacion («Motivos de cancelación»)` |
| 386 | menú menu | `/administracion/migrar-anio («Migrar año»)` |
| 387 | menú menu | `/administracion/posiciones («Posiciones»)` |
| 388 | menú menu | `/administracion/proveedores («Proveedores»)` |
| 389 | menú menu | `/administracion/respaldos («Respaldos»)` |
| 390 | menú menu | `/administracion/notificaciones («Notificaciones»)` |
| 391 | menú menu | `/administracion/tarifas-cobro («Tarifas de cobro»)` |
| 396 | menú menu | `/administracion/personal («Usuarios»)` |
| 420 | src | `/static/branding/colibri-icono.png` |
| 425 | menú nav | `/anunciar («Anunciar»)` |
| 426 | menú nav | `/consultar («Consultar»)` |
| 440 | menú nav | `/mis-paquetes («Mis paquetes»)` |
| 441 | menú nav | `/mis-datos («Mis datos»)` |
| 447 | menú nav | `/paquetes («Paquetes»)` |
| 448 | menú nav | `/residentes («Residentes»)` |
| 457 | href | `/entrar` |
| 482 | action | `/bloquear` |
| 487 | action | `/salir-dispositivo` |
| 523 | menú nav_footer | `/anunciar («Anunciar»)` |
| 524 | menú nav_footer | `/consultar («Consultar»)` |
| 525 | menú nav_footer | `/ayuda («Ayuda»)` |
| 537 | menú nav_footer | `/mis-paquetes («Mis paquetes»)` |
| 538 | menú nav_footer | `/mis-datos («Mis datos»)` |
| 544 | menú nav_footer | `/announce («Anunciar»)` |
| 546 | menú nav_footer | `/paquetes («Paquetes»)` |
| 547 | menú nav_footer | `/residentes («Residentes»)` |
| 565 | href | `https://jemavi.co` |
| 778 | js | `/paquetes/` |

### `como_funciona/form.html`

| Línea | Tipo | Destino |
|---|---|---|
| 13 | src | `/static/branding/papyrus-logo.png` |
| 35 | href | `/anunciar` |
| 41 | href | `/consultar` |
| 47 | href | `/entrar` |
| 48 | href | `/mis-paquetes` |
| 48 | href | `/mis-datos` |
| 60 | href | `/terminos` |
| 80 | href | `/privacidad` |
| 88 | href | `/ayuda` |

### `components/_botones.html`

| Línea | Tipo | Destino |
|---|---|---|
| 18 | hx-post | `/paquetes/1/cancelar` |

### `components/_busqueda_filtros.html`

| Línea | Tipo | Destino |
|---|---|---|
| 309 | href | `/announce` |

### `components/_capa_bloqueo.html`

| Línea | Tipo | Destino |
|---|---|---|
| 26 | href | `/ingresar` |
| 157 | js | `/bloqueo` |

### `components/_carga_fotos.html`

| Línea | Tipo | Destino |
|---|---|---|
| 189 | js | `/paquetes/` |

### `components/_confirmacion.html`

| Línea | Tipo | Destino |
|---|---|---|
| 25 | href | `/consultar` |
| 26 | href | `/otp` |

### `components/_formulario_persona_nueva.html`

| Línea | Tipo | Destino |
|---|---|---|
| 41 | action | `/announce` |

### `components/_formularios.html`

| Línea | Tipo | Destino |
|---|---|---|
| 12 | action | `/anunciar` |

### `components/_inputs.html`

| Línea | Tipo | Destino |
|---|---|---|
| 178 | href | `/terminos` |

### `components/_modales.html`

| Línea | Tipo | Destino |
|---|---|---|
| 20 | action | `/paquetes/{{ p.id }}/recibir` |
| 32 | action | `/paquetes/` |

### `components/_persona_resuelta.html`

| Línea | Tipo | Destino |
|---|---|---|
| 84 | action | `/announce` |
| 142 | href | `/paquetes?recibir={{ p.id }}` |

### `components/_recibir_paquete.html`

| Línea | Tipo | Destino |
|---|---|---|
| 50 | action | `/paquetes/{{ paquete_id }}/recibir` |
| 249 | js | `/paquetes/{{ paquete_id }}/nuevo-residente/identificar?contacto=` |
| 474 | js | `/paquetes/` |
| 900 | js | `/paquetes/guia-repetida?guia=` |
| 1042 | src | `/static/vendor/zxing.min.js` |

### `cookies/form.html`

| Línea | Tipo | Destino |
|---|---|---|
| 14 | src | `/static/branding/papyrus-logo.png` |
| 85 | href | `/terminos` |
| 88 | href | `/privacidad` |
| 96 | href | `/ayuda` |

### `customer/aceptar_terminos.html`

| Línea | Tipo | Destino |
|---|---|---|
| 14 | href | `/terminos` |
| 16 | action | `/mis-datos/aceptar-terminos` |

### `customer/paquetes.html`

| Línea | Tipo | Destino |
|---|---|---|
| 116 | href | `/consultar?q={{ p.access_code }}` |

### `customer/verify.html`

| Línea | Tipo | Destino |
|---|---|---|
| 45 | href | `/consultar?q={{ codigo|urlencode }}` |
| 110 | action | `/mis-datos` |
| 131 | href | `/terminos` |
| 138 | href | `/privacidad` |
| 222 | action | `/mis-datos/eliminar-cuenta` |
| 357 | action | `/mis-datos/ocupantes/{{ ocupante.id }}/confirmar` |
| 377 | action | `/mis-datos/ocupantes/` |
| 409 | action | `/mis-datos/ocupantes/{{ ocupante.id }}/editar` |
| 450 | action | `/mis-datos/ocupantes/{{ ocupante.id }}/notificaciones` |
| 483 | action | `/mis-datos/ocupantes/{{ ocupante.id }}/contacto` |
| 494 | action | `/mis-datos/ocupantes` |
| 551 | action | `/mis-datos/ocupantes/salir` |

### `customers_manage/_resultados.html`

| Línea | Tipo | Destino |
|---|---|---|
| 53 | href | `/residentes/{{ o.persona_id }}` |
| 178 | href | `/residentes/{{ p.id }}` |
| 243 | href | `/paquetes?q={{ p.termino_busqueda_paquetes|urlencode }}` |
| 264 | href | `/residentes/{{ p.id }}?tab=residentes` |
| 274 | href | `/residentes/{{ f.vive_con_persona_id }}?tab=residentes` |
| 599 | action | `/residentes/` |
| 616 | action | `/residentes/{{ p.id }}/apartamento` |

### `customers_manage/detail.html`

| Línea | Tipo | Destino |
|---|---|---|
| 32 | href | `/residentes` |
| 137 | action | `/residentes/` |
| 228 | action | `/residentes/{{ persona.id }}/saldo-contra-entrega/movimiento` |
| 249 | href | `/consultar?q={{ m.paquete_access_code }}` |
| 290 | action | `/residentes/{{ persona.id }}` |
| 339 | action | `/residentes/{{ persona.id }}/apartamento` |
| 387 | action | `/residentes/{{ persona.id }}/notificaciones` |
| 474 | href | `/residentes/{{ o.persona_id }}?tab=residentes` |
| 547 | action | `/residentes/{{ persona.id }}/ocupantes/{{ o.id }}/confirmar` |
| 584 | href | `/residentes/{{ o.persona_id }}?tab=notif` |
| 611 | action | `/residentes/{{ persona.id }}/ocupantes/{{ o.id }}/editar` |
| 660 | action | `/residentes/{{ persona.id }}/ocupantes` |
| 808 | js | `/residentes/{{ persona.id }}/ocupantes/identificar?contacto=` |

### `customers_manage/movimientos_saldo_contra_entrega.html`

| Línea | Tipo | Destino |
|---|---|---|
| 17 | href | `/residentes/saldos-contra-entrega` |
| 20 | action | `/residentes/movimientos-saldo-contra-entrega` |
| 51 | href | `/residentes/{{ m.persona_id }}` |
| 58 | href | `/consultar?q={{ m.paquete_access_code }}` |

### `customers_manage/saldos_contra_entrega.html`

| Línea | Tipo | Destino |
|---|---|---|
| 10 | href | `/residentes/movimientos-saldo-contra-entrega` |
| 13 | action | `/residentes/saldos-contra-entrega` |
| 23 | href | `/residentes/{{ persona.id }}` |

### `packages/_acciones.html`

| Línea | Tipo | Destino |
|---|---|---|
| 164 | href | `tel:{{ p.recipient_phone }}` |
| 168 | href | `tel:{{ p.persona_anunciante.telefono }}` |
| 186 | href | `mailto:{{ p.persona_anunciante.email }}` |

### `packages/_resultados.html`

| Línea | Tipo | Destino |
|---|---|---|
| 147 | href | `/consultar?q={{ p.access_code }}` |
| 172 | href | `tel:{{ _tel_contacto }}` |
| 337 | href | `/residentes/{}` |
| 337 | href | `/consultar?q={}` |
| 362 | href | `tel:{{ p.recipient_phone }}` |
| 399 | href | `/residentes/{{ p.persona_destino_id }}?tab=residentes` |
| 552 | href | `mailto:{{ r.persona.email }}` |
| 584 | action | `/paquetes/` |
| 596 | action | `/paquetes/{{ p.id }}/asignar-apartamento` |
| 662 | action | `/paquetes/{{ p.id }}/corregir` |
| 822 | js | `/paquetes/{{ p.id }}/nuevo-residente/identificar?contacto=` |
| 915 | action | `/paquetes/promover-principal` |
| 969 | action | `/paquetes/{{ p.id }}/entregar` |

### `privacy/form.html`

| Línea | Tipo | Destino |
|---|---|---|
| 17 | src | `/static/branding/papyrus-logo.png` |
| 70 | href | `/cookies` |
| 127 | href | `/mis-datos` |
| 157 | href | `/ayuda` |

### `routes/admin.py`

| Línea | Tipo | Destino |
|---|---|---|
| 229 | redirect | `/administracion/personal?creado={creado.id}` |
| 265 | redirect | `/administracion/personal` |

### `routes/admin_respaldos.py`

| Línea | Tipo | Destino |
|---|---|---|
| 189 | redirect | `/administracion/respaldos` |

### `routes/announce.py`

| Línea | Tipo | Destino |
|---|---|---|
| 98 | redirect | `/anunciar` |
| 307 | redirect | `/anunciar/confirmacion?id={paquete.id}` |

### `routes/auth.py`

| Línea | Tipo | Destino |
|---|---|---|
| 122 | redirect | `/mi-pin` |
| 174 | redirect | `/paquetes` |
| 207 | redirect | `/ingresar` |
| 248 | redirect | `/bloqueo` |
| 300 | redirect | `/anunciar` |

### `routes/customer_auth.py`

| Línea | Tipo | Destino |
|---|---|---|
| 74 | redirect | `/mis-datos` |
| 139 | redirect | `/otp/verificar?telefono={normalizar_telefono(telefono)}` |
| 188 | redirect | `/otp` |

### `routes/customer_verify.py`

| Línea | Tipo | Destino |
|---|---|---|
| 318 | redirect | `/mis-datos` |
| 431 | redirect | `/otp?telefono_actualizado=1` |
| 433 | redirect | `/mis-datos?guardado=1` |
| 511 | redirect | `/otp?cuenta_eliminada=1` |
| 557 | redirect | `/mis-datos?ocupante_guardado=1` |

### `routes/customers_manage.py`

| Línea | Tipo | Destino |
|---|---|---|
| 1359 | redirect | `/residentes/{persona.id}?ocupante_guardado=1` |
| 1740 | redirect | `/residentes?eliminado=1` |

### `routes/entrar.py`

| Línea | Tipo | Destino |
|---|---|---|
| 34 | redirect | `/paquetes` |
| 36 | redirect | `/mis-datos` |

### `routes/packages.py`

| Línea | Tipo | Destino |
|---|---|---|
| 1784 | redirect | `/paquetes?recibir={paquete.id}&aviso=recepcion_pendiente` |
| 1866 | redirect | `/paquetes?aviso=residente_sin_apartamento` |
| 2039 | redirect | `/paquetes` |
| 2189 | redirect | `/paquetes?corregir={paquete.id}&aviso=residente_pendiente` |

### `routes/password_reset.py`

| Línea | Tipo | Destino |
|---|---|---|
| 175 | redirect | `/ingresar?restablecida=1` |

### `search/form.html`

| Línea | Tipo | Destino |
|---|---|---|
| 19 | src | `/static/branding/papyrus-logo.png` |
| 25 | action | `/consultar` |
| 72 | href | `/otp` |
| 176 | href | `/consultar?q={}` |
| 213 | action | `/paquetes/{{ paquete.id }}/entregar` |
| 319 | href | `/consultar?q={{ c.access_code|urlencode }}` |

### `terms/form.html`

| Línea | Tipo | Destino |
|---|---|---|
| 23 | src | `/static/branding/papyrus-logo.png` |
| 40 | href | `/privacidad` |
| 45 | href | `/como-funciona` |
| 130 | href | `/consultar` |
| 130 | href | `/mis-paquetes` |
| 145 | href | `/mis-datos` |
| 187 | href | `/ayuda` |

### `web/app.py`

| Línea | Tipo | Destino |
|---|---|---|
| 133 | redirect | `/anunciar` |

### `web/security.py`

| Línea | Tipo | Destino |
|---|---|---|
| 291 | redirect | `/mis-datos/aceptar-terminos` |

### `web/templates/admin/conjunto.html`

| Línea | Tipo | Destino |
|---|---|---|
| 19 | macro | `/administracion/conjunto` |
| 33 | macro | `/administracion/conjunto/empresa` |
| 43 | macro | `/administracion/conjunto/seguridad` |

### `web/templates/admin/motivos_anulacion_cobro.html`

| Línea | Tipo | Destino |
|---|---|---|
| 13 | macro | `/administracion/motivos-anulacion-cobro` |
| 28 | macro | `/administracion/motivos-anulacion-cobro/X/eliminar` |

### `web/templates/admin/motivos_bloqueo.html`

| Línea | Tipo | Destino |
|---|---|---|
| 13 | macro | `/administracion/motivos-bloqueo` |
| 28 | macro | `/administracion/motivos-bloqueo/X/eliminar` |

### `web/templates/admin/motivos_cancelacion.html`

| Línea | Tipo | Destino |
|---|---|---|
| 20 | macro | `/administracion/motivos-cancelacion` |
| 52 | macro | `/administracion/motivos-cancelacion/X/eliminar` |

### `web/templates/admin/posiciones.html`

| Línea | Tipo | Destino |
|---|---|---|
| 13 | macro | `/administracion/posiciones` |

### `web/templates/admin/tarifas_cobro.html`

| Línea | Tipo | Destino |
|---|---|---|
| 11 | macro | `/administracion/tarifas-cobro` |

### `web/templates/announce/form.html`

| Línea | Tipo | Destino |
|---|---|---|
| 17 | macro | `/anunciar` |

### `web/templates/auth/customer_login.html`

| Línea | Tipo | Destino |
|---|---|---|
| 14 | macro | `/otp/solicitar` |

### `web/templates/auth/login.html`

| Línea | Tipo | Destino |
|---|---|---|
| 16 | macro | `/ingresar` |

### `web/templates/auth/me.html`

| Línea | Tipo | Destino |
|---|---|---|
| 30 | macro | `/mi-sesion/editar` |
| 42 | macro | `/mi-sesion` |

### `web/templates/auth/olvide_password.html`

| Línea | Tipo | Destino |
|---|---|---|
| 14 | macro | `/staff/olvide-password` |

### `web/templates/auth/pin.html`

| Línea | Tipo | Destino |
|---|---|---|
| 17 | macro | `/mi-pin` |

### `web/templates/auth/restablecer_password.html`

| Línea | Tipo | Destino |
|---|---|---|
| 14 | macro | `/staff/restablecer-password` |

### `web/templates/components/_estado_vacio.html`

| Línea | Tipo | Destino |
|---|---|---|
| 16 | macro | `/anunciar` |

### `web/templates/components/_formularios.html`

| Línea | Tipo | Destino |
|---|---|---|
| 12 | macro | `/anunciar` |

### `web/templates/components/_modales.html`

| Línea | Tipo | Destino |
|---|---|---|
| 32 | macro | `/paquetes/X/cancelar` |

### `web/templates/customer/verify.html`

| Línea | Tipo | Destino |
|---|---|---|
| 222 | macro | `/mis-datos/eliminar-cuenta` |
| 377 | macro | `/mis-datos/ocupantes/X/baja` |
| 399 | macro | `/mis-datos/ocupantes/X/promover` |
| 551 | macro | `/mis-datos/ocupantes/salir` |

### `web/templates/customers_manage/_resultados.html`

| Línea | Tipo | Destino |
|---|---|---|
| 599 | macro | `/residentes/X/eliminar` |

### `web/templates/customers_manage/detail.html`

| Línea | Tipo | Destino |
|---|---|---|
| 137 | macro | `/residentes/X/reactivar` |
| 144 | macro | `/residentes/X/baja-administrativa` |
| 156 | macro | `/residentes/X/bloquear` |
| 196 | macro | `/residentes/X/autorizar-desbloqueo` |
| 214 | macro | `/residentes/X/liberar-bloqueo` |
| 608 | macro | `/residentes/X/ocupantes/X/baja` |
| 652 | macro | `/residentes/X/ocupantes/X/promover` |

### `web/templates/packages/_resultados.html`

| Línea | Tipo | Destino |
|---|---|---|
| 584 | macro | `/paquetes/X/eliminar` |
| 1121 | macro | `/paquetes/X/cancelar` |
| 1165 | macro | `/announce` |

### `web/templates/search/form.html`

| Línea | Tipo | Destino |
|---|---|---|
| 25 | macro | `/consultar` |