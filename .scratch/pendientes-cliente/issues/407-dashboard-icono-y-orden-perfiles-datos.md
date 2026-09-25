# 407 — Menú de cuenta: ícono propio para "Dashboard" y Perfiles antes que Datos

**Pedido original (Jesús):** "Cambia el ícono de dashboard a uno mejor que se te ocurra, no como el de buscar que
tiene ahora, adicional cambia el orden o posición de 'datos y perfiles'".

**Status:** desplegado en test (`c77c719`), pendiente confirmar en vivo

## Decisiones

- "Dashboard": ícono de gráfico de barras (`iconos_nav.dashboard`, nuevo) en vez de la lupa de buscar.
- Categorías: Perfiles primero, Datos después.

## Verificación

- `test_layout.py`: la prueba del Dashboard ahora exige el ícono de barras (no la lupa) y Perfiles antes que Datos. 32 en verde.
