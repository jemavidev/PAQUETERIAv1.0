# 62 — Menú de cuenta: agregar Consultar y Ayuda (debajo de Mis paquetes/Mis datos, arriba de Cerrar sesión)

**Pedido original (cliente):** "Incluye la vista de '/consultar', '/ayuda'
respectivamente al NAV menu de la version mobile, quedaria debajo de 'Mis
datos', 'Mis paquetes' y arriba de 'Cerrar session'."

Contexto: pedido en respuesta a un hallazgo propio (auditoría de header/
footer pedida por el cliente) -- al mover Consultar/Ayuda fuera del footer
móvil del cliente en [[61]], quedaron sin ninguna vía alcanzable desde
mobile.

**Status:** implementado

## Contexto

El menú de cuenta (avatar/dropdown) es un solo bloque compartido, se ve
igual en mobile y desktop -- no existe hoy un mecanismo para que tenga
contenido distinto por resolución sin agregar JS/complejidad nueva.
Aclarado con el cliente antes de implementar: Consultar/Ayuda van al mismo
bloque compartido `bloque_cliente()`, así que también van a aparecer en
desktop (ahí ya eran alcanzables por otro lado -- Consultar en
`.site-nav`, Ayuda en el footer de escritorio -- acá quedan como acceso
extra, no un problema).

## Implementación

`bloque_cliente()` (`app/web/templates/base.html`) gana 2 líneas nuevas al
final:

```jinja
{{ enlace_menu('/mis-paquetes', 'Mis paquetes', iconos_nav.paquetes, contorno=true) }}
{{ enlace_menu('/mis-datos', 'Mis datos', iconos_nav.mis_datos) }}
{{ enlace_menu('/consultar', 'Consultar', iconos_nav.buscar) }}
{{ enlace_menu('/ayuda', 'Ayuda', iconos_nav.ayuda, contorno=true) }}
```

Como `bloque_cliente()` se llama justo antes del separador +
"Cerrar sesión" en el `<details class="account-menu">`, el orden final
queda exactamente Mis paquetes → Mis datos → Consultar → Ayuda → (línea)
→ Cerrar sesión, como se pidió.

## Verificación

- Sintaxis Jinja verificada con `Environment.parse()`.
- `tests/web/test_layout.py`: test nuevo que verifica presencia de los 2
  enlaces y el orden completo de los 5 elementos (incluye "Cerrar
  sesión") dentro de `.account-menu-panel` -- 26/26 en el archivo.
- Suite completa (`tests/data_model tests/web`): 637/637, sin regresiones.
- Sin clases Tailwind nuevas -- no hizo falta recompilar `tailwind.css`.
- Pendiente: confirmar en `test.papyrus.com.co` que el menú de cuenta
  muestra los 4 enlaces en el orden pedido, tanto en mobile como desktop.
