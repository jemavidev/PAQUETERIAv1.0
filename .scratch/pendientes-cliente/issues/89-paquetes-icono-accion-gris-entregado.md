# 89 — `/paquetes` columna Acciones: ícono de Acción gris para Entregados

**Pedido original (cliente):**
"por el dia de hoy necesito solo un cambio mas, para los paquetes
entregados coloca el icono en la columana de accion de color gris o
desactivado para que no sea cliqueable y gris tipo desactivado"

**Status:** implementado

## Contexto

Revierte, solo para el estado ENTREGADO, parte de un pedido anterior
del mismo día (conversación 2026-08-14, issue 79): "todos los iconos
siempre tengan colores... me refiero a los iconos de los estados
Anunciado, recibido, entregado y cancelado" -- ese pedido coloreaba el
ícono de Acción también en los estados terminales (verde en Entregado,
rojo en Cancelado) en vez de apagarlo a gris. Hoy el cliente pidió lo
contrario específicamente para Entregado.

## Implementación

- `packages/_acciones.html`: el ícono de Acción (check) en ENTREGADO
  pasa de `text-emerald-600` a `text-slate-300` -- mismo tono ya usado
  para WhatsApp/Teléfono/Email cuando no hay dato. Ya era no-clicable
  (`<span>`, no `<button>`) desde antes; el cambio es puramente de
  color.
- CANCELADO se queda rojo (`text-red-600`) -- no fue parte de este
  pedido, que fue explícito sobre "los paquetes entregados".

## Verificación

- `tests/web/test_packages.py`: 95 tests pasan (ninguno afirmaba el
  color emerald anterior).
- Verificación visual con Playwright (captura de una fila Entregado
  real): check gris, junto al lápiz también gris; la X de Cancelar
  se mantiene roja.
- Pendiente: deploy a test.papyrus.com.co.
