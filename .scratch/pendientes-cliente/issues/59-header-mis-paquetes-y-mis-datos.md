# 59 — Header: "Mis paquetes"/"Mis datos" en el menú de cuenta + 4ta opción en desktop

**Pedido original (cliente):** "1- Necesito que en el header del DESKTOP y
MOBILE se pueda visualizar en el NAV menu (o la seccion del meno de
hamburguesa) las opciones de 'Mis paquetes y Mis Datos' uno debajo del
otro. 2- De igual forma necesito que solo en el DESKTOP se pueda
visualizar 4 opciones en el menu que serian (Anunciar, Consultar, Mis
Paquetes y Mis Datos) [...] Ten en cuenta que desde el MOBILE mode no se
va a visualizar los nombres como tal, solo se mostrara en las opciones del
dropdown del nav menu (hamburguesa)."

Alcance confirmado por el cliente tras restatement en texto (sin
AskUserQuestion esta vez, "dime si me entiendes todo" + "si"): agregar
"Mis paquetes"+"Mis datos" al menú de cuenta (dropdown del avatar, se ve
igual en mobile y desktop) y agregar "Mis datos" como 4ta opción de
`.site-nav` (oculto en mobile, solo desktop) -- sin duplicar
Anunciar/Consultar dentro del menú de cuenta (esos ya están en el footer
móvil).

**Status:** implementado

## Contexto

Antes de este pedido: "Mis paquetes" solo vivía en `.site-nav` (oculto en
mobile) -- no había NINGUNA forma de llegar ahí desde el header/menú en un
celular. "Mis datos" solo vivía en el menú de cuenta (avatar, dropdown),
nunca en `.site-nav`.

## Implementación

`app/web/templates/base.html`:

- `enlace_menu()` (el macro que arma cada ítem del menú de cuenta) ganó un
  parámetro `contorno` (mismo patrón ya usado en `enlace_nav`/
  `enlace_nav_footer`) -- necesario porque `iconos_nav.paquetes` es un
  ícono de trazo (outline, viewBox 24x24), no de relleno (solid, viewBox
  20x20) como el resto de los ítems de ese menú.
- `bloque_cliente()`: agrega `enlace_menu('/mis-paquetes', 'Mis paquetes',
  iconos_nav.paquetes, contorno=true)` antes del `enlace_menu` existente de
  "Mis datos" -- quedan uno debajo del otro en el menú de cuenta, que se
  ve igual en mobile y desktop.
- `.site-nav` del cliente (`{% if tiene_persona %}`): agrega
  `enlace_nav('/mis-datos', 'Mis datos', iconos_nav.mis_datos)` como 4ta
  opción, después de Anunciar/Consultar/Mis paquetes -- sigue oculto en
  mobile (`@media (max-width:767px) { .site-nav { display:none; } }`, sin
  tocar).

Sin clases nuevas de Tailwind (todo el header usa CSS plano en el
`<style>` de `base.html`) -- no hizo falta recompilar `tailwind.css`.

## Verificación

- `tests/web/test_layout.py`: 2 tests nuevos (`.account-menu-panel`
  contiene ambos enlaces en el orden pedido; `.site-nav` tiene las 4
  opciones) -- 24/24 en el archivo.
- Docstring de `test_footer_movil_del_cliente_repite_los_enlaces_de_su_audiencia`
  actualizado -- ya no es cierto que "Mis paquetes"/"Mis datos" solo vivan
  en el nav de escritorio.
- Suite completa (`tests/data_model tests/web`): 635/635, sin regresiones.
- Pendiente: confirmar en `test.papyrus.com.co` que el menú de cuenta
  (mobile y desktop) muestra ambos enlaces uno debajo del otro, y que
  `.site-nav` de escritorio muestra las 4 opciones.
