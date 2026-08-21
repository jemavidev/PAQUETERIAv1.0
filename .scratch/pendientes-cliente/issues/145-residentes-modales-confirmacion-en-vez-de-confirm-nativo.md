# 145 — `/residentes`: modales de confirmación en vez de `confirm()` nativo

**Pedido original:** "Arregla la inconsistencia de los confirm(), ten presente que la base de
cómo se tiene que manejar todo tiene que estar en compliance con las vistas de /paquetes y
/anuncios" -- encontrado durante un análisis pedido de la vista `/residentes`: la ficha
(`customers_manage/detail.html`) usaba `confirm()` nativo del navegador para "Rechazar/Eliminar"
residente y "Convertir en residente principal", mientras `search.html` (misma ruta) y `/paquetes`
ya usaban el componente `modal_confirmacion` para sus acciones equivalentes (Eliminar
cliente/paquete, Cancelar paquete).

**Status:** implementado

## Decisiones de implementación

- **Rechazar/Eliminar residente**: `modal_confirmacion(..., variant='danger')` -- mismo criterio
  que "Eliminar cliente" (`search.html`) y "Eliminar paquete"/"Cancelar paquete" (`/paquetes`).
  Texto dinámico según `o.confirmado_en` (Rechazar si pendiente, Eliminar si ya confirmado),
  igual que el `confirm()` que reemplaza.
- **Convertir en residente principal**: `modal_confirmacion(..., variant='warning')` -- primer uso
  real del rol `warning` del componente (existía en `components/_modales.html` pero nadie lo
  usaba todavía). No es destructivo como Eliminar, pero sí un cambio de estado real (degrada
  automáticamente al principal actual), así que amerita su propio tono, no genérico `danger`.
  Reutiliza literalmente la frase "se degrada automáticamente a quien es principal ahora" del
  modal "Promover a otro residente" de `/paquetes` (`packages/_resultados.html`), para que el
  lenguaje de esa misma acción sea idéntico en ambas vistas.
- Toggle `data-open`/`data-close` agregado a `detail.html` (no existía -- la ficha no usaba
  ningún modal de este componente todavía): mismo contrato simple (`querySelectorAll(...).forEach`)
  que ya usan `search.html`/`admin/staff.html`, no el patrón delegado sobre `document` de
  `/paquetes` (ese existe ahí porque `#resultados-paquetes` se reemplaza dinámicamente; la ficha
  de `/residentes` es siempre un render de página completa, no lo necesita).

## Verificación

- Sintaxis Jinja (`Environment.parse()`) sobre ambas plantillas -- OK.
- `tests/web/test_customers_manage.py`: 92/92 sin regresiones.
- Render real contra `localhost:8010` (staff logueado, ficha con un Ocupante secundario sin
  confirmar): confirmado en el HTML devuelto que no queda ningún `onsubmit="return confirm(...)"`,
  ambos modales renderizan con texto/color correcto y los `data-open`/`id` calzan.
- Pendiente: confirmación visual en navegador real (sin acceso a la extensión Chrome en esta
  sesión) -- verificado solo por HTML devuelto por el servidor, no por captura de pantalla.
