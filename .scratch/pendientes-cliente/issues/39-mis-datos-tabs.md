# 39 — `/mis-datos`: reorganizar en pestañas (Datos/Notificaciones/Apartamento/Ocupantes)

**Pedido original (cliente):** "necesito 4 variantes llamativas... orientadas
a UX, para mayor facilidad de hacer las cosas" (prototipo de 4 variantes,
`prototype` skill) → "creo que la opcion A es la mejor, aplica esta a esta
vista de mis datos".

**Status:** verificado

## Contexto

Prototipo con 4 variantes construido aparte (sin tocar la app real) para que
el cliente decidiera: A) tabs por sección, B) resumen + acordeón, C) panel
lateral tipo configuración, D) edición en línea. Eligió **A**.

## Implementación

`customer/verify.html`: las 4 tarjetas apiladas (Datos personales,
Notificaciones, Mi apartamento, Mis Ocupantes/Quiénes más viven acá) pasan a
un layout de pestañas — una franja con avatar+nombre+teléfono arriba, y una
barra de 3 o 4 pestañas (la de Ocupantes solo aparece si la Persona es
principal o Ocupante no-principal de algún apartamento).

Puramente visual/cliente (JS vanilla, sin tocar `customer_verify.py`):
Datos/Notificaciones/Apartamento siguen viviendo dentro del MISMO `<form>`
de siempre (una sola llamada `POST /mis-datos`) — las pestañas solo alternan
`display:none` sobre cada panel; un panel oculto igual manda sus campos al
enviar el formulario, así que "Guardar" sigue guardando las 3 secciones
juntas sin importar en cuál quedó el usuario. "Mis Ocupantes"/"Quiénes más
viven acá" ya eran un bloque aparte (sus propios `<form>` por acción) y pasan
a ser la 4ta pestaña tal cual.

Pestaña inicial calculada en el servidor según el contexto del re-render:
error en Torre/Apartamento → pestaña Apartamento; error en Teléfono/Email →
Datos; `ocupante_guardado=1` → Ocupantes; si no, Datos por defecto — para no
perder de vista en qué parte del formulario ocurrió un error tras enviar.

Sin cambios de backend, sin migraciones, sin tests nuevos (nada de lógica de
servidor cambió — mismos campos, mismos endpoints, mismas validaciones).

## Verificación

Render real verificado localmente (servidor + Postgres efímero sembrado con
un principal + 2 Ocupantes, sesión forjada para saltar el flujo OTP) — no
solo revisión de código. Capturas de las 4 pestañas y de mobile (390px)
confirmaron:
- Avatar/nombre/teléfono arriba, pestañas con la activa resaltada.
- Notificaciones: Llamada/WhatsApp deshabilitados y marcados correctamente.
- Apartamento y Ocupantes con su contenido intacto.
- **Encontrado y corregido en esta verificación**: el botón "Guardar" (del
  form de Datos/Notificaciones/Apartamento) quedaba visible incluso en la
  pestaña Ocupantes, donde no aplica — ahora se oculta junto con esas 3
  pestañas (`#form-guardar-wrap`, mismo mecanismo de `activar()`).
- Mobile: la barra de pestañas hace scroll horizontal cuando no caben las 4
  (`overflow-x-auto` ya existente), sin romper el layout.

Tailwind recompilado (clases `w-11`/`h-11`/etc. del avatar y la barra de
pestañas no estaban en el CSS ya compilado) — cache-bust `?v=26` → `?v=27`.
