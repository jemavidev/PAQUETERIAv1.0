# 01 — Atajo de anuncio solo-por-teléfono para clientes conocidos en `/anunciar`

**What to build:** un cliente en `/anunciar` cuyo teléfono ya tiene al menos 1 paquete `ENTREGADO` histórico puede anunciar un paquete nuevo escribiendo solo su Teléfono + aceptando Términos y Condiciones, sin que se le pida Nombre — el paquete queda anunciado a su nombre ya registrado. Un cliente cuyo teléfono no califica sigue viendo el pedido de Nombre exactamente como hoy (aparece tras el primer intento sin nombre, sin perder lo ya escrito). El límite existente de 10 anuncios activos por teléfono sigue aplicando igual para ambos caminos.

**Blocked by:** Ninguno — puede arrancar de inmediato.

**Status:** ready-for-agent

- [ ] `GET /anunciar` inicial muestra solo Teléfono + Términos, sin el campo Nombre visible.
- [ ] `POST` con un teléfono que ya tiene ≥1 paquete `ENTREGADO` histórico, sin nombre, con términos aceptados → crea el Paquete `ANUNCIADO` con el nombre YA REGISTRADO de esa Persona.
- [ ] `POST` con un teléfono sin ningún `ENTREGADO` histórico, sin nombre → no crea el paquete; re-renderiza mostrando el campo Nombre + mensaje pidiéndolo, preservando teléfono y aceptación de términos.
- [ ] Reenviar ese mismo teléfono ahora con nombre sí crea el paquete (flujo actual, sin cambios de comportamiento).
- [ ] Un teléfono con solo paquetes `ANUNCIADO`/`RECIBIDO`/`CANCELADO` (nunca `ENTREGADO`) sigue tratándose como NO conocido.
- [ ] El límite de 10 anuncios activos y la pantalla intermedia "ya tienes N, ¿continuar?" siguen aplicando igual para el camino sin nombre.
- [ ] Un teléfono con formato inválido sigue fallando con el mismo error de hoy, antes de evaluar si es conocido.
- [ ] `CONTEXT.md` actualiza la definición de "Anuncio" para reflejar que el Nombre es condicional (solo obligatorio si el teléfono no es ya conocido).

## Referencias

- Spec: `.scratch/anunciar-atajo-telefono-conocido/spec.md`
- Reutiliza `es_primera_entrega_a_telefono` (issue 314, `.scratch/pendientes-cliente`) negada como criterio de "cliente conocido".
