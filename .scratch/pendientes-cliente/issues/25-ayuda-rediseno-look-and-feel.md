# 25 — `/ayuda`: rediseño de look and feel + enlaces reales

**Pedido original (cliente):** "ya la mayoría del contenido está allí, PERO
no tiene un buen look and feel así como se vería en
https://paquetex.papyrus.com.co/help, dime cómo puedes mejorarlo de esta
misma manera, adiciona a esto quiero que identifiques los links que se usan
en esta vista, si los tenemos, asócialos, pero si no los tenemos contempla
la creación de los mismos a futuro." + 2 correcciones de íconos en el
camino: versión clara (no oscura) del ícono de Anunciar para esta vista, y
confirmación del ícono de WhatsApp (ya era el correcto, sin cambios).

**Vista:** `ayuda/form.html` + `icons.py` (nuevo ícono `rayo`, `ayuda`
corregido a outline).

**Status:** verificado

## Decisiones confirmadas con el cliente

- Íconos SVG outline del design system (no emoji, para no romper
  consistencia con el resto del rebuild) -- **confirmado**.
- FAQ como acordeón (`<details>/<summary>` nativo, mismo patrón que
  `cuenta_menu()` de `base.html`, sin JS) en vez de tarjetas siempre
  abiertas -- **confirmado**.

## Inventario de enlaces (producción → rebuild)

| Producción | Rebuild | Estado |
|---|---|---|
| `/announce` | `/anunciar` | ✓ ya existe |
| `/search` | `/consultar` | ✓ ya existe |
| `/auth/login`, `/customer/verify` | `/entrar` (ambas pestañas) → `/mis-datos` | ✓ ya existe, mejor flujo (OTP 2 dígitos) |
| `tel:+573334004007` | mismo número real (`WHATSAPP_SOPORTE_NUMERO` ya configurado) | ✓ ya existe |
| `wa.me/573334004007` | mismo, ya en el footer | ✓ ya existe |
| `mailto:paquetex@papyrus.com.co` | mismo buzón (ticket 15) | ✓ agregado como botón nuevo |
| `/terms` | `/terms` | ✓ ya existe, agregado como tarjeta |
| `/privacy` | — | ✗ NO existe -- pendiente crear |
| `/cookies` | — | ✗ NO existe -- pendiente crear |
| `jemavi.co` | ya en el footer | ✓ ya existe |

## Qué se hizo

- Logo de Papyrus arriba (mismo tratamiento que el resto de vistas
  públicas).
- Encabezado tipo "hero": ícono de Ayuda en badge circular azul + "Centro
  de Ayuda" + subtítulo.
- Tarjeta intro "¿Qué es PAQUETEX?" con 3 pilares (Confiable/Rápido/Fácil),
  íconos SVG en color claro dentro de mini-tarjetas.
- Las 11 preguntas (6 del rebuild + 5 nuevas sobre cómo funciona/código de
  seguimiento/notificaciones/autogestión/seguridad) como acordeón.
- 3 tarjetas de acción (Anunciar/Consultar/Contactar) con badges de color
  CLARO -- el ícono de "Anunciar" (mismo path que ya existía en
  `iconos_nav.anunciar`) ahora se ve en `text-emerald-600` sobre
  `bg-emerald-100`, no oscuro.
- Tarjeta de contacto con botón de llamar + botón nuevo de correo
  (`mailto:paquetex@papyrus.com.co`).
- Tarjeta de Términos y Condiciones (único enlace legal real hoy).
- `icons.py`: ícono `rayo` nuevo (Heroicons bolt outline). Confirmado que
  el ícono de WhatsApp YA era el path exacto que pediste -- sin cambios
  ahí.
- Recompilado `tailwind.css` (`group-open:*`, `open:*`, varios colores
  nuevos) + bump de cache-busting a `v=18`. Test `test_get_ayuda_no_
  requiere_sesion` actualizado (el texto cambió de "Preguntas frecuentes"
  a "Centro de Ayuda"). Verificado con un render aislado (`TestClient` +
  `file://`, incluyendo abrir un acordeón) antes de tocar el sitio en vivo.

## Pendiente (a futuro, según lo pedido)

`/privacy` y `/cookies` no existen todavía -- quedan fuera de esta ronda a
propósito ("contempla la creación de los mismos a futuro"). Cuando se
haga, mismo patrón que `/terms` (página estática, placeholder razonable,
no revisión legal).

## Verificación

- [x] Captura confirma el nuevo look and feel (mobile y desktop),
      acordeón funcionando, tarjetas de acción con íconos claros.
- [x] Suite de tests completa sin regresiones (454 passed).
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo.
