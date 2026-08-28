# 197 — `/mi-sesion` ("Mi perfil"): mejora visual

**Pedido original (cliente):**
"mejora el como se ve esta vista /mi-sesion, ya que se ve poco profesional
y no acorde con lo que hemos venido trabajando, solucionalo"

**Status:** implementado

## Qué estaba desalineado del resto del sistema

- El `<h1>` vivía DENTRO de la tarjeta blanca (`text-lg`), a diferencia de
  `/administracion/personal` y `/administracion/notificaciones`, donde el
  título de página es `text-xl`, vive AFUERA de cualquier tarjeta, como
  primer elemento del contenedor.
- Nombre/Email/Rol se mostraban como una `<dl>` plana sin ningún
  tratamiento visual -- el resto del sistema usa avatar+badge de color
  para identidad (ver el propio dropdown de cuenta en el header) y pills
  redondeadas para el rol (`admin/staff.html`, tabla de Perfiles).
- El contenedor usaba `py-10` (el resto de pantallas de una columna usa
  `py-8`).
- El botón "Cerrar sesión" no era `full_width`, a diferencia del resto de
  botones únicos de una tarjeta en el sistema.

## Implementación

- Contenedor y `<h1>` alineados exactamente al patrón de
  `/administracion/notificaciones` (`max-w-md mx-auto px-4 py-8 space-y-4`
  + `<h1 class="text-xl font-bold text-slate-900">` afuera de la tarjeta).
- Tarjeta de identidad: avatar circular (inicial del nombre, `bg-blue-800`,
  mismo azul de marca que el resto de botones primarios) + Nombre + Email,
  badge de Rol con los MISMOS colores exactos que ya usa la tabla de
  Perfiles (`admin/staff.html`: índigo para ADMIN, gris para OPERADOR) en
  vez de texto plano.
- "Cerrar sesión" pasa a `full_width=True`.
- Las 2 tarjetas de formulario ([[196]], [[198]]) pasan de `<div>` a mano a
  `formulario_flujo` -- el macro que ya usan `/anunciar`,
  `/staff/restablecer-password`, etc., mismo tratamiento de tarjeta+título.

## Verificación

- Mismos tests de [[196]]/[[198]] (no hay lógica nueva acá, solo markup) --
  siguen pasando sin tocarlos.
- Verificado en vivo contra el servidor de dev local.
- Pendiente: deploy a test.papyrus.com.co.
