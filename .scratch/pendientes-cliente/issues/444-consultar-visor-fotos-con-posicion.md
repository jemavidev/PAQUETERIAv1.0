# 444 — `/consultar?q=<código>`: ícono y Posición en el visor de fotos

**Pedido original (Jesús, 2026-10-11):** "Agregar el icono de la posicion en la vista /consultar?q=<codigo de paquete>
cuando se visualizan las imagenes, la idea de esto es ver como se ve el paquete y con el icono y la posicion se veria
donde esta ubicada."

**Status:** implementado (local, 2026-10-11) — Jesús pidió centrarla; falta verificar el centrado y desplegar

## Decisiones

- `galeria_fotos(fotos, visor_id, posicion=none)` (`components/_visor_fotos.html`): con `posicion`, el visor ampliado
  muestra arriba a la izquierda una píldora violeta grande `📍 <posición>`, la misma de `components/_posicion.html`
  en tamaño `text-xl`, para leerla sobre el fondo oscuro.
- En `/consultar` se pasa con el mismo criterio que la píldora junto a los días (issues 427/431): **solo con sesión de
  staff y solo RECIBIDO**. El residente nunca la ve, y en Entregado/Cancelado ya no hay posición vigente.
- Prueba: `tests/web/test_search.py::test_visor_de_fotos_muestra_la_posicion_solo_al_staff_y_solo_recibido`.

## Seguimiento

- Jesús (2026-10-11): "podrías centrar la píldora con la posición". Pasa de arriba a la izquierda a **arriba al
  centro** (`left-1/2 -translate-x-1/2`, mismo centrado que el contador "1 / 3" de abajo).
