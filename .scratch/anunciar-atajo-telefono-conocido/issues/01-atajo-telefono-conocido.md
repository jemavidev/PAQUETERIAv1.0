# 01 — Atajo de anuncio solo-por-teléfono para clientes conocidos en `/anunciar`

**What to build:** un cliente en `/anunciar` cuyo teléfono ya tiene al menos 1 paquete `ENTREGADO` histórico puede anunciar un paquete nuevo escribiendo solo su Teléfono + aceptando Términos y Condiciones, sin que se le pida Nombre — el paquete queda anunciado a su nombre ya registrado. Un cliente cuyo teléfono no califica sigue viendo el pedido de Nombre exactamente como hoy (aparece tras el primer intento sin nombre, sin perder lo ya escrito). El límite existente de 10 anuncios activos por teléfono sigue aplicando igual para ambos caminos.

**Blocked by:** Ninguno — puede arrancar de inmediato.

**Status:** implementado -- pendiente que el cliente lo confirme visualmente en vivo (no desplegado a test.papyrus.com.co todavía).

- [x] `GET /anunciar` inicial muestra solo Teléfono + Términos, sin el campo Nombre visible.
- [x] `POST` con un teléfono que ya tiene ≥1 paquete `ENTREGADO` histórico, sin nombre, con términos aceptados → crea el Paquete `ANUNCIADO` con el nombre YA REGISTRADO de esa Persona.
- [x] `POST` con un teléfono sin ningún `ENTREGADO` histórico, sin nombre → no crea el paquete; re-renderiza mostrando el campo Nombre + mensaje pidiéndolo, preservando teléfono y aceptación de términos.
- [x] Reenviar ese mismo teléfono ahora con nombre sí crea el paquete (flujo actual, sin cambios de comportamiento).
- [x] Un teléfono con solo paquetes `ANUNCIADO`/`RECIBIDO`/`CANCELADO` (nunca `ENTREGADO`) sigue tratándose como NO conocido.
- [x] El límite de 10 anuncios activos y la pantalla intermedia "ya tienes N, ¿continuar?" siguen aplicando igual para el camino sin nombre.
- [x] Un teléfono con formato inválido sigue fallando con el mismo error de hoy, antes de evaluar si es conocido.
- [x] `CONTEXT.md` actualiza la definición de "Anuncio" para reflejar que el Nombre es condicional (solo obligatorio si el teléfono no es ya conocido).

## Referencias

- Spec: `.scratch/anunciar-atajo-telefono-conocido/spec.md`
- Reutiliza `es_primera_entrega_a_telefono` (issue 314, `.scratch/pendientes-cliente`) negada como criterio de "cliente conocido".

## Code-review (dos ejes) antes de comitear

- **Eje spec:** faltaba testear el camino "conocido + sin nombre" contra el límite de 10 anuncios activos/pantalla `confirmar_multiple`, y el caso `RECIBIDO`-only -- agregados. También encontró que `mostrar_nombre` se recalculaba desde cero en cada POST (`bool(nombre.strip())`), así que si el cliente tropezaba con OTRO campo antes de escribir su nombre, el campo Nombre podía "desaparecer" de nuevo -- corregido con un hidden field `mostrar_nombre` que lo deja pegajoso una vez revelado.
- **Eje standards:** `_error()` recibía `mostrar_nombre` como parámetro en cada call site (6 lugares repitiendo `mostrar_nombre=mostrar_nombre`) -- refactorizado para que cierre sobre la variable externa directamente, eliminando el riesgo de que un futuro branch de error "olvide" pasarlo.

## Bug encontrado en vivo tras implementar (reportado por el cliente)

Al pedir el Nombre (teléfono no conocido), el checkbox de Términos y Condiciones aparecía SIN marcar en el re-render, aunque el cliente ya lo había aceptado -- de hecho la aceptación es la razón por la que se llegó a pedir el Nombre en vez de fallar antes por Términos. El checkbox nunca tuvo lógica de `checked` en NINGÚN re-render (bug latente desde antes de este ticket, pero invisible mientras Nombre+Teléfono+Términos vivían siempre juntos -- ahora que pedir el Nombre es el camino esperado para un teléfono nuevo, se volvió visible de inmediato). Corregido: `acepta_tyc` se agrega a `valores` (el dict que ya preserva teléfono/nombre en cada re-render) y el template ahora emite `checked` condicionalmente. 3 tests nuevos (`test_acepta_tyc_permanece_marcado_al_pedir_nombre`, `test_acepta_tyc_no_marcado_en_carga_limpia`, `test_acepta_tyc_no_marcado_si_no_se_acepto`), verificado en vivo contra el servidor de desarrollo con el mismo escenario reportado (teléfono `3000000000`).
