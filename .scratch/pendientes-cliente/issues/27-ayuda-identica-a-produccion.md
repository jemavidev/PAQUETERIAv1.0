# 27 — `/ayuda`: réplica IDÉNTICA de producción (no solo "similar")

**Pedido original (cliente):** "veo que no has sido capaz de hacer lo que
te pido con relación a la vista de /ayuda, NECESITO QUE SEA IGUAL EN LOOK
AND FEEL A https://paquetex.papyrus.com.co/help... crees que puedes hacer
que sea IGUAL, sin cambiar nada, solo dime que necesitas para que sea
IGUAL" → confirmé los 4 puntos necesarios (emoji, secciones de negocio,
colores exactos, tipografía exacta) → **"SI QUE SEA IDENTICO"**.

**Vista:** `ayuda/form.html` — reescritura completa.

**Status:** verificado

## Qué se hizo

Extraje el HTML completo servido por `paquetex.papyrus.com.co/help` (vía
Playwright, no un resumen) y reconstruí la plantilla copiando LITERAL las
clases de Tailwind, textos, emoji y estructura de cada sección:

- Logo + hero "❓ Centro de Ayuda" con emoji grande.
- "📦 ¿Qué es PAQUETEX?" con 3 pilares (🛡️⚡📱).
- "🕐 Horarios de Atención" (Lun-Vie/Sáb/Dom) con aviso amarillo.
- "💰 Tarifas del Servicio" (Paquete Normal $1,500 COP / Extra
  Dimensionado $2,000 COP / Almacenamiento $1,000 COP por día) +
  "Ejemplo de Cálculo" -- info de negocio que el software no gestiona
  todavía, incluida de todas formas porque el pedido explícito fue
  paridad visual exacta, no paridad de features.
- 9 preguntas de acordeón (antes tenía 6, con contenido distinto) --
  "Cómo funciona", "Cuánto tiempo para recoger", "Código de seguimiento",
  "Cómo busco mi paquete", "Qué notificaciones recibiré", "Cómo puedo
  pagar", "Mi paquete está seguro", "Cómo gestiono mis preferencias",
  "Cómo contacto con soporte" -- contenido, emoji y colores por pregunta
  copiados literal.
- 3 tarjetas de acción con degradado (verde/púrpura/azul) + emoji
  grandes.
- Tarjeta de contacto con botones de teléfono/correo.
- 3 tarjetas legales con emoji (📜🔒🍪).

**Única diferencia intencional**: el acordeón de producción usa Alpine.js
(`x-data`/`@click`/`x-show`) -- el rebuild no tiene esa dependencia
(ADR-0004: vanilla por defecto) y agregarla solo para esto sería una
decisión de arquitectura mayor, no pedida. Se usa `<details>/<summary>`
nativo -- mismo resultado visual e interactivo (confirmado con captura:
abre/cierra igual, mismo ícono de flecha rotando), sin JS nuevo.

Enlaces internos corregidos a nuestras rutas reales (`/anunciar`,
`/consultar`, `/entrar` en vez de `/customer/verify` con código de 6
dígitos -- el nuestro es de 2).

Recompilado `tailwind.css` (decenas de clases nuevas: gradientes,
`hover:-translate-y-1`, colores por sección) + bump de cache-busting a
`v=20`. Verificado con un render aislado, comparado directamente contra
capturas reales de producción sección por sección, antes de tocar el
sitio en vivo.

## Verificación

- [x] Suite de tests completa sin regresiones (454 passed).
- [x] Capturas confirman paridad visual sección por sección contra
      producción (mobile y desktop).
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo.
